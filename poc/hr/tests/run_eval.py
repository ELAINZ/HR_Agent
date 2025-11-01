import json
from agent_platform.router.basic_router import BasicRouter
from agent_platform.router.llm_router import LLMRouter
from agent_platform.core.executor import Executor
from agent_platform.core.evaluator import Evaluator
from agent_platform.core.debugger import analyze_failures
from agent_platform.core.reporter import save_json, generate_html_report
def main():
    router = LLMRouter()
    executor = Executor()
    evaluator = Evaluator()

    with open("poc/hr/tests/testcases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    results = []
    for case in cases:
        predicted_api = router.plan(case["query"])
        eval_result = evaluator.evaluate(case, predicted_api)
        results.append(eval_result)

    errors = analyze_failures(results)
    save_json(results, "poc/hr/tests/report.json")
    generate_html_report(results, "poc/hr/tests/report.html")

    print(f" 测试完成: {len(results)} 条, 失败 {len(errors)} 条。报告已生成。")

if __name__ == "__main__":
    main()
