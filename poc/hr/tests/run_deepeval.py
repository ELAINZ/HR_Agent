"""
使用 DeepEval 对 HR Agent 的路由效果进行评测

- 复用现有的 testcases.json
- 使用 BasicRouter / LLMRouter 输出 predicted_api
- 自定义 RouterAccuracyMetric 作为指标
"""

import json
import os
from typing import List

from deepeval import evaluate
from deepeval.test_case import LLMTestCase

from agent_platform.router.llm_router import LLMRouter
from agent_platform.core.deepeval_metrics import RouterAccuracyMetric


def build_test_cases() -> List[LLMTestCase]:
    """
    将现有的测试用例转成 DeepEval 的 LLMTestCase
    - input: 用户 query
    - actual_output: 路由计划出的 API
    - expected_output: 预期 API（来自 testcases.json 的 expected_api 字段）
    """
    router = LLMRouter()

    here = os.path.dirname(__file__)
    cases_path = os.path.join(here, "testcases.json")
    with open(cases_path, "r", encoding="utf-8") as f:
        cases = json.load(f)

    test_cases: List[LLMTestCase] = []
    for case in cases:
        query = case["query"]
        expected_api = case["expected_api"]

        predicted_api = router.plan(query)

        test_cases.append(
            LLMTestCase(
                input=query,
                actual_output=predicted_api,
                expected_output=expected_api,
                # 下面字段可选，只是方便在报告中看到更多信息
                retrieval_context=case.get("context", []),
                metadata={"id": case.get("id"), "category": case.get("category")},
            )
        )

    return test_cases


def main():
    test_cases = build_test_cases()

    metric = RouterAccuracyMetric()

    print(f"共构建 {len(test_cases)} 条 DeepEval 测试用例，开始评测...")
    evaluate(test_cases=test_cases, metrics=[metric])

    overall = metric.get_result()
    if overall is not None:
        print(f"\nRouter Accuracy: {overall * 100:.2f}%")


if __name__ == "__main__":
    main()


