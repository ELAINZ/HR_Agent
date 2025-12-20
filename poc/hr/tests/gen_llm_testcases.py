"""
使用 LLM 自动扩充 routing 测试数据集

数据来源：
- 输入：agent_platform/injection/api_registry.json（每个 API 的 purpose / params / 示例）
- 输出：poc/hr/tests/generated_testcases.json（LLM 生成的新用例）

用法（在项目根目录执行）：
    python poc/hr/tests/gen_llm_testcases.py

注意：
- 使用 Moonshot（或兼容 OpenAI API 协议的服务），读取环境变量 MOONSHOT_API_KEY
- 不会修改现有的 testcases.json，只是生成一个新的文件，方便你人工审阅 / 合并
"""

import json
import os
import uuid
from typing import List, Dict

from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()


def build_client() -> OpenAI:
    api_key = os.getenv("MOONSHOT_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("请在环境变量中配置 MOONSHOT_API_KEY 或 OPENAI_API_KEY 用于生成数据集")

    # 如果你用的是 Moonshot，则需要 base_url；如果是 OpenAI 官方，可以去掉 base_url
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.moonshot.cn/v1")
    return OpenAI(api_key=api_key, base_url=base_url)


def load_api_registry() -> List[Dict]:
    here = os.path.dirname(__file__)
    root = os.path.abspath(os.path.join(here, "../../.."))
    registry_path = os.path.join(root, "agent_platform/injection/api_registry.json")
    with open(registry_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_prompt(api: Dict, n_positive: int, n_negative: int) -> str:
    return f"""
你现在在帮我为一个 HR API 路由器生成**中文查询示例**，用于训练/评测“query → API” 的映射。

API 信息：
- 路径: {api["api"]}
- 功能描述: {api.get("purpose", "")}
- 参数: {", ".join(api.get("params", []))}

已有的 positive 示例（应该路由到这个 API）：
{json.dumps(api["examples"]["positive"], ensure_ascii=False, indent=2)}

已有的 negative 示例（不应该路由到这个 API，或者属于其他 API）：
{json.dumps(api["examples"]["negative"], ensure_ascii=False, indent=2)}

请你：
1. 生成 {n_positive} 条 **新的 positive 查询**，语义要多样化，覆盖不同说法、不同场景，但都应该路由到同一个 API。
2. 生成 {n_negative} 条 **新的 negative 查询**，这些查询要看起来“合理”，但属于其他 API 或无法确定路由到该 API。
3. 所有输出必须是有效 JSON，格式如下（不要多余解释）：
{{
  "positive": ["...", "..."],
  "negative": ["...", "..."]
}}
"""


def ask_llm_for_examples(
    client: OpenAI,
    api: Dict,
    model: str = None,
    n_positive: int = 5,
    n_negative: int = 3,
) -> Dict[str, List[str]]:
    model = model or os.getenv("DATASET_LLM_MODEL", "moonshot-v1-8k")
    prompt = build_prompt(api, n_positive=n_positive, n_negative=n_negative)

    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个严谨的数据生成助手，只输出符合要求的 JSON。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )
    content = resp.choices[0].message.content.strip()

    try:
        data = json.loads(content)
        pos = [str(x).strip() for x in data.get("positive", []) if str(x).strip()]
        neg = [str(x).strip() for x in data.get("negative", []) if str(x).strip()]
        return {"positive": pos, "negative": neg}
    except Exception as e:
        print(f"[WARN] 无法解析 LLM 输出为 JSON，跳过该 API: {api['api']}, error={e}")
        print("LLM 原始输出：", content[:500])
        return {"positive": [], "negative": []}


def make_testcase(q: str, api_path: str, label: str) -> Dict:
    return {
        "id": str(uuid.uuid4())[:8],
        "query": q,
        "expected_api": api_path if label == "positive" else "other",
        "label": label,
    }


def main():
    client = build_client()
    apis = load_api_registry()

    all_cases: List[Dict] = []

    for api in apis:
        print(f"== 处理 API: {api['api']} ==")
        gen = ask_llm_for_examples(client, api)

        for q in gen["positive"]:
            all_cases.append(make_testcase(q, api["api"], "positive"))
        for q in gen["negative"]:
            all_cases.append(make_testcase(q, api["api"], "negative"))

        print(f"  + 生成 positive: {len(gen['positive'])}, negative: {len(gen['negative'])}")

    here = os.path.dirname(__file__)
    out_path = os.path.join(here, "generated_testcases.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_cases, f, ensure_ascii=False, indent=2)

    print(f"\n✓ LLM 生成的数据集已写入: {out_path}")
    print(f"  共 {len(all_cases)} 条用例。你可以人工审阅后，决定是否合并到 testcases.json。")


if __name__ == "__main__":
    main()


