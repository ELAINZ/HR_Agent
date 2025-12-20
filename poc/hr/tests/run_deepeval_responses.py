"""
使用 DeepEval 同时评测：
1. 路由是否正确（RouterAccuracyMetric）
2. 返回 JSON 数据是否符合预期结构 / 关键字段（JSONResponseMetric）

评测数据来源：
- 路由用例：poc/hr/tests/testcases.json
- 返回值规范：poc/hr/tests/response_specs.json（按 case id 关联）
"""

import json
import os
import sys
from typing import List, Dict

# 确保可以从任意工作目录 / 运行环境导入 agent_platform
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from deepeval import evaluate
from deepeval.test_case import LLMTestCase

from agent_platform.router.llm_router import LLMRouter
from agent_platform.core.executor import Executor
from agent_platform.core.deepeval_metrics import RouterAccuracyMetric, JSONResponseMetric


def _load_cases() -> List[Dict]:
    here = os.path.dirname(__file__)
    cases_path = os.path.join(here, "testcases.json")
    with open(cases_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_response_specs() -> Dict[str, Dict]:
    """
    将 response_specs.json 转成 {case_id: spec} 的形式，便于快速查找。
    """
    here = os.path.dirname(__file__)
    spec_path = os.path.join(here, "response_specs.json")
    if not os.path.exists(spec_path):
        return {}

    with open(spec_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    mapping: Dict[str, Dict] = {}
    for item in items:
        cid = item.get("id")
        if cid:
            mapping[cid] = item.get("spec", {})
    return mapping


def build_test_cases() -> List[LLMTestCase]:
    router = LLMRouter()
    executor = Executor()

    raw_cases = _load_cases()
    spec_map = _load_response_specs()

    test_cases: List[LLMTestCase] = []

    for case in raw_cases:
        cid = case["id"]
        query = case["query"]
        expected_api = case["expected_api"]

        # 1. 路由规划
        predicted_api = router.plan(query)

        # 2. 实际调用后端，拿到 JSON 返回
        response_json = None
        try:
            resp, _latency = executor.execute(case_id=cid, query=query, route_plan=predicted_api)
            response_json = resp
        except Exception as e:
            # 请求失败时，response_json 保持为 None，JSONResponseMetric 会打低分
            response_json = {"__error__": str(e)}

        # 3. 找到该 case 对应的返回值规范（如果有）
        response_spec = spec_map.get(cid, {})

        # 4. 构造 DeepEval 的测试用例
        #    - DeepEval 的 LLMTestCase 要求 actual_output / expected_output 均为字符串
        #    - 我们这里把 JSON 和 spec 都序列化为字符串，JSONResponseMetric 内部会再反序列化
        from json import dumps
        actual_output_str = dumps(response_json, ensure_ascii=False)
        expected_output_str = dumps(response_spec, ensure_ascii=False) if response_spec else "{}"
        test_cases.append(
            LLMTestCase(
                input=query,
                actual_output=actual_output_str,   # 给 JSONResponseMetric 用（字符串形式）
                expected_output=expected_output_str,  # JSONResponseMetric 会处理为 dict
                metadata={
                    "id": cid,
                    "expected_api": expected_api,
                    "predicted_api": predicted_api,
                },
            )
        )

    return test_cases


def main():
    test_cases = build_test_cases()

    router_metric = RouterAccuracyMetric()
    json_metric = JSONResponseMetric()

    print(f"共构建 {len(test_cases)} 条 DeepEval 测试用例，开始评测（路由 + 返回数据）...")
    evaluate(test_cases=test_cases, metrics=[router_metric, json_metric])

    router_overall = router_metric.get_result()
    if router_overall is not None:
        print(f"\nRouter Accuracy: {router_overall * 100:.2f}%")

    # JSONResponseMetric 自身不做聚合，这里只是提示完成
    print("JSONResponseMetric 评测完成（详见 DeepEval 输出明细）。")


if __name__ == "__main__":
    main()


