def analyze_failures(results):
    errors = []
    for r in results:
        if not r["pass"]:
            reason = "路由错误" if r["predicted"] != r["expected"] else "未知错误"
            errors.append({
                "case_id": r["id"],
                "query": r["query"],
                "expected": r["expected"],
                "predicted": r["predicted"],
                "reason": reason
            })
    return errors
