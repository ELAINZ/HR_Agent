from typing import List, Optional, Dict, Any

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class RouterAccuracyMetric(BaseMetric):
    """
    自定义 DeepEval 指标：
    - 只关心路由是否将 query 映射到正确的 API（expected_output）
    - 不调用额外的 LLM，评估快速、可离线运行
    """

    def __init__(self, name: str = "router_accuracy"):
        # 注意：当前版本的 BaseMetric 没有自定义 __init__，直接设置属性即可
        self.name = name
        self.total = 0
        self.correct = 0

    def measure(self, test_case: LLMTestCase) -> float:
        """
        返回当前用例的得分（0 或 1）
        """
        self.total += 1
        passed = int((test_case.actual_output or "") == (test_case.expected_output or ""))
        self.correct += passed
        return float(passed)

    def is_successful(self, score: float) -> bool:
        """
        DeepEval 会用该函数判断单个用例是否通过
        """
        return score >= 1.0

    def get_result(self) -> Optional[float]:
        """
        返回整体准确率，用于聚合展示
        """
        if self.total == 0:
            return None
        return self.correct / self.total


class JSONResponseMetric(BaseMetric):
    """
    针对「返回数据」的结构化评测指标（不依赖 LLM）：
    - 检查必须存在的字段（has_keys）
    - 检查若干字段值是否与预期一致（equals）

    约定：
    - test_case.actual_output: 实际返回的 JSON（dict 或 JSON 字符串）
    - test_case.expected_output: 期望规范（spec），形如：
        {
          "has_keys": ["employee_id", "annual_leave_remaining"],
          "equals": {"employee_id": "E12345"}
        }
    """

    def __init__(self, name: str = "json_response"):
        self.name = name

    @staticmethod
    def _ensure_dict(obj: Any) -> Dict[str, Any]:
        import json

        if isinstance(obj, dict):
            return obj
        if isinstance(obj, str):
            try:
                return json.loads(obj)
            except Exception:
                return {}
        return {}

    def measure(self, test_case: LLMTestCase) -> float:
        actual = self._ensure_dict(test_case.actual_output)
        spec = self._ensure_dict(test_case.expected_output)

        if not spec:
            # 没有提供规范，则不打分（记为 1.0，避免影响总分）
            return 1.0

        has_keys: List[str] = spec.get("has_keys", []) or []
        equals: Dict[str, Any] = spec.get("equals", {}) or {}

        total_checks = len(has_keys) + len(equals)
        if total_checks == 0:
            return 1.0

        passed = 0

        # 检查必备字段
        for k in has_keys:
            if k in actual:
                passed += 1

        # 检查字段值一致性
        for k, v in equals.items():
            if k in actual and actual.get(k) == v:
                passed += 1

        return passed / total_checks

    def is_successful(self, score: float) -> bool:
        # 可以根据需要调整阈值，这里要求全部通过
        return score >= 1.0


class HallucinationRuleMetric(BaseMetric):
    """
    简单的“幻觉”检测指标（不依赖 LLM）：

    约定：
    - test_case.actual_output: 实际返回（dict / JSON 字符串 / 纯文本）
    - test_case.expected_output: 行为规范，形如：
        {
          "behavior": "should_not_hallucinate",  # 或 "not_found", "normal" 等
          "allow_numbers": false                 # 可选：是否允许出现大量具体数字
        }

    基本规则（可按需扩展）：
    - behavior == "should_not_hallucinate":
        - 期望回答中包含“未知 / 暂无 / 不清楚 / 未找到”这类安全词之一
        - 不能同时出现明显“编造”的模式（大量具体数字且没有任何安全词）
    - 其他 behavior：当前默认直接返回 1.0，不影响总体分数
    """

    def __init__(self, name: str = "hallucination_rule"):
        self.name = name

        # 可以根据业务自己调整这些词表
        self.safe_keywords = ["暂无", "未找到", "没有相关", "不清楚", "不支持", "无法提供", "未知"]

    @staticmethod
    def _ensure_text(obj: Any) -> str:
        import json

        if isinstance(obj, str):
            # 有可能是 JSON 字符串，也可能是纯文本
            try:
                data = json.loads(obj)
                # 尝试从常见字段中拼接文本
                if isinstance(data, dict):
                    texts = []
                    if "message" in data:
                        texts.append(str(data["message"]))
                    if "snippets" in data and isinstance(data["snippets"], list):
                        for s in data["snippets"]:
                            if isinstance(s, dict) and "text" in s:
                                texts.append(str(s["text"]))
                    if texts:
                        return "\n".join(texts)
                return obj
            except Exception:
                return obj

        if isinstance(obj, dict):
            texts = []
            if "message" in obj:
                texts.append(str(obj["message"]))
            if "snippets" in obj and isinstance(obj["snippets"], list):
                for s in obj["snippets"]:
                    if isinstance(s, dict) and "text" in s:
                        texts.append(str(s["text"]))
            if texts:
                return "\n".join(texts)
            return json.dumps(obj, ensure_ascii=False)

        return str(obj or "")

    @staticmethod
    def _ensure_spec(obj: Any) -> Dict[str, Any]:
        import json

        if isinstance(obj, dict):
            return obj
        if isinstance(obj, str):
            try:
                return json.loads(obj)
            except Exception:
                return {}
        return {}

    def measure(self, test_case: LLMTestCase) -> float:
        text = self._ensure_text(test_case.actual_output)
        spec = self._ensure_spec(test_case.expected_output)

        behavior = spec.get("behavior")
        if not behavior:
            # 未指定行为标签，则不参与打分
            return 1.0

        # 只对“应该不要乱说”的场景做检查
        if behavior == "should_not_hallucinate":
            text_lower = text.lower()
            has_safe = any(k in text for k in self.safe_keywords)

            # 粗略判断“具体数字”数量
            import re

            numbers = re.findall(r"\d+", text_lower)
            many_numbers = len(numbers) >= 3

            # 策略：
            # - 如果包含安全词（“暂无/未找到”等），认为通过
            # - 如果没有任何安全词且出现了很多数字，认为高风险幻觉，打 0 分
            if has_safe:
                return 1.0
            if many_numbers:
                return 0.0

            # 其他情况暂时认为通过（可以根据需要变严）
            return 1.0

        # 其他行为暂不做限制
        return 1.0

    def is_successful(self, score: float) -> bool:
        # 只要被判为“高风险幻觉”（score=0）就视为失败
        return score >= 1.0
