"""
使用 DeepEval 进行综合评测，包括：
1. 路由是否正确（RouterAccuracyMetric）
2. 返回 JSON 数据是否符合预期结构（JSONResponseMetric）
3. 是否存在幻觉（HallucinationRuleMetric）

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
from agent_platform.core.deepeval_metrics import (
    RouterAccuracyMetric, 
    JSONResponseMetric,
    HallucinationRuleMetric
)


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
            # 请求失败时，response_json 保持为 None
            response_json = {"__error__": str(e)}

        # 3. 找到该 case 对应的返回值规范（如果有）
        response_spec = spec_map.get(cid, {})
        
        # 4. 构建幻觉检测规范
        # 如果 response_spec 中有 behavior 字段，用于幻觉检测
        # 否则，对于某些查询类型，可以自动推断是否需要检测幻觉
        hallucination_spec = {}
        if "behavior" in response_spec:
            hallucination_spec = {"behavior": response_spec["behavior"]}
        elif expected_api == "/hr/policy" or "政策" in query or "查询" in query:
            # 对于政策查询类，如果返回了具体数字但没有安全词，可能是幻觉
            hallucination_spec = {"behavior": "should_not_hallucinate"}

        # 5. 构造 DeepEval 的测试用例
        from json import dumps
        actual_output_str = dumps(response_json, ensure_ascii=False)
        
        # expected_output 用于 JSONResponseMetric（结构验证）
        json_spec = {
            "has_keys": response_spec.get("has_keys", []),
            "equals": response_spec.get("equals", {})
        }
        expected_output_str = dumps(json_spec, ensure_ascii=False) if json_spec.get("has_keys") or json_spec.get("equals") else "{}"
        
        # 为 HallucinationRuleMetric 准备数据
        # 我们将 hallucination_spec 放在 metadata 中，然后在测试用例中处理
        test_cases.append(
            LLMTestCase(
                input=query,
                actual_output=actual_output_str,   # 给 JSONResponseMetric 和 HallucinationRuleMetric 用
                expected_output=expected_output_str,  # JSONResponseMetric 会处理为 dict
                retrieval_context=[],  # 可选
                metadata={
                    "id": cid,
                    "expected_api": expected_api,
                    "predicted_api": predicted_api,
                    "hallucination_spec": hallucination_spec,  # 幻觉检测规范
                },
            )
        )

    return test_cases


class HallucinationMetricWrapper(HallucinationRuleMetric):
    """
    包装器：从 metadata 中读取 hallucination_spec
    """
    def measure(self, test_case: LLMTestCase) -> float:
        import json
        # 从 metadata 中获取幻觉检测规范
        hallucination_spec = test_case.metadata.get("hallucination_spec", {})
        if not hallucination_spec or not hallucination_spec.get("behavior"):
            return 1.0  # 没有规范，不参与打分
        
        # 创建临时测试用例用于幻觉检测
        from deepeval.test_case import LLMTestCase as TempTestCase
        
        temp_case = TempTestCase(
            input=test_case.input,
            actual_output=test_case.actual_output,
            expected_output=json.dumps(hallucination_spec)
        )
        
        # 调用父类方法
        return super().measure(temp_case)


def main():
    test_cases = build_test_cases()

    router_metric = RouterAccuracyMetric()
    json_metric = JSONResponseMetric()
    hallucination_metric = HallucinationMetricWrapper()

    print(f"共构建 {len(test_cases)} 条 DeepEval 测试用例，开始评测（路由 + 返回数据 + 幻觉检测）...")
    evaluate(test_cases=test_cases, metrics=[router_metric, json_metric, hallucination_metric])

    router_overall = router_metric.get_result()
    if router_overall is not None:
        print(f"\n✅ Router Accuracy: {router_overall * 100:.2f}%")

    # 统计幻觉检测结果
    hallucination_failures = 0
    for test_case in test_cases:
        score = hallucination_metric.measure(test_case)
        if score < 1.0:
            hallucination_failures += 1
    
    total_with_spec = sum(1 for tc in test_cases if tc.metadata.get("hallucination_spec"))
    if total_with_spec > 0:
        hallucination_rate = (total_with_spec - hallucination_failures) / total_with_spec * 100
        print(f"✅ Hallucination Detection: {hallucination_rate:.2f}% ({total_with_spec - hallucination_failures}/{total_with_spec} passed)")
        if hallucination_failures > 0:
            print(f"⚠️  发现 {hallucination_failures} 条可能的幻觉回答")

    print("\n✅ JSONResponseMetric 评测完成（详见 DeepEval 输出明细）。")


if __name__ == "__main__":
    main()

