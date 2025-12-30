import difflib
from typing import Dict
import os
from openai import OpenAI
from dotenv import load_dotenv
import time
load_dotenv()

class Evaluator:
    """
    LLM-Assisted Evaluator:
    - 基于静态规则 + LLM 解释的混合评估器
    """

    def __init__(self, model="moonshot-v1-8k"):
        self.client = OpenAI(
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url="https://api.moonshot.cn/v1"  # ✅ 改成你的 Moonshot endpoint
        )
        self.model = model

    def evaluate(self, case: Dict, predicted_api: str) -> Dict:
        try:
            expected = case.get("expected_api")
            query = case.get("query")
            case_id = case.get("id")

            # 规范化字符串比较：去除首尾空格
            expected_clean = (expected or "").strip()
            predicted_clean = (predicted_api or "").strip()
            
            passed = (predicted_clean == expected_clean)
            error_reason = "" if passed else self._analyze_error(query, expected_clean, predicted_clean)

            return {
                "id": case_id,
                "query": query,
                "expected": expected_clean,
                "predicted": predicted_clean,
                "pass": passed,
                "error": error_reason
            }
        except Exception as e:
            # 如果评估过程中出现任何错误，返回错误结果
            return {
                "id": case.get("id", "unknown"),
                "query": case.get("query", ""),
                "expected": case.get("expected_api", ""),
                "predicted": predicted_api or "",
                "pass": False,
                "error": f"评估过程出错: {str(e)}"
            }

    def _analyze_error(self, query: str, expected: str, predicted: str) -> str:
        """
        自动生成 LLM 辅助错误解释
        """

        # === 静态名称映射 ===
        def name(api_path: str):
            mapping = {
                "/hr/leave/balance": "假期余额查询",
                "/hr/leave/apply": "请假申请",
                "/hr/policy": "HR 政策查询",
                "/hr/benefits/list": "福利清单查询",
                "/hr/benefits/apply": "福利申请",
                "/hr/expense/submit": "报销申请",
                "/hr/travel/policy": "差旅政策查询",
                "/hr/travel/apply": "出差申请",
                "/hr/attendance/checkin": "打卡签到",
                "/hr/attendance/status": "出勤状态查询",
                "/hr/payroll/info": "工资查询",
                "/hr/payroll/tax": "个税与社保查询",
                "/hr/profile/view": "个人档案查看",
                "/hr/profile/update": "个人信息修改",
                "/hr/training/list": "培训课程列表查询",
                "/hr/training/apply": "培训报名",
                "/hr/recruitment/referral": "内推推荐",
                "/hr/recruitment/openings": "招聘岗位查询",
                "/hr/contract/view": "合同查看",
                "/hr/contract/renew": "合同续签"
            }
            return mapping.get(api_path, api_path or "未知API")

        # === 规则优先部分 ===
        if predicted in [None, "", "other"]:
            return f"应是【{name(expected)}】，但未匹配到任何 API。"

        # 相似度检测
        similarity = difflib.SequenceMatcher(None, expected, predicted).ratio()
        if similarity > 0.8:
            return f"应是【{name(expected)}】，实际识别为【{name(predicted)}】，路径高度相似（{similarity:.2f}），可能是路由细节混淆。"

        # === 交给 LLM 生成自然语言分析 ===
        prompt = f"""
你是一个智能评估助手。  
我将给你一个用户的输入问题、一条预期的API路径、以及模型预测的API路径。  
请简短说明预测错误的原因（比如“将假期余额问题误识别为政策查询”）。  
输出中文一句话。

用户输入：{query}
预期API：{expected}（{name(expected)}）
实际预测：{predicted}（{name(predicted)}）

请用一句中文描述错误原因。
"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个精确、简洁的错误分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                timeout=30  # 设置超时时间，避免长时间等待
            )
            reason = resp.choices[0].message.content.strip()
        except Exception as e:
            # LLM调用失败时，返回基于规则的错误分析
            reason = f"应是【{name(expected)}】，实际识别为【{name(predicted)}】，请检查路由逻辑。（LLM解释失败：{str(e)[:100]}）"

        return reason
