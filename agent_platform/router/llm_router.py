import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import time
load_dotenv()

class LLMRouter:
    def __init__(self, model="moonshot-v1-8k", registry_path="agent_platform/injection/api_registry.json"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请先设置环境变量 OPENAI_API_KEY")

        #  使用 OpenAI SDK 指向 Moonshot API endpoint
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.moonshot.cn/v1"
        )

        self.model = model
        with open(registry_path, "r", encoding="utf-8") as f:
            self.apis = json.load(f)

    def plan(self, query: str):
        # 构造选项列表（简化且结构化）
        options = "\n".join(
            [f"{api['api']}：{api['purpose']}" for api in self.apis]
        )

        prompt = f"""
你是一个智能HR系统的路由规划器（API Router）。
下面是所有可用的API及其功能：
{options}

请根据用户的输入，选择最合适的API路径（只输出路径字符串，不解释）。

用户问题：
“{query}”

输出格式：
仅输出一个API路径，例如：
/hr/leave/balance
"""

        # 使用 responses.create（新 SDK 写法）
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个精确的 API 分类助手。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        time.sleep(20)

        # 提取 LLM 输出结果
        text = resp.choices[0].message.content.strip()
        # 清理格式符号
        text = text.split()[0].strip("`'\"，。 ")
        return text
