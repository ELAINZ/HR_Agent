# tools/gen_testcases_from_registry.py
import json, uuid

with open("./agent_platform/injection/api_registry.json", "r", encoding="utf-8") as f:
    apis = json.load(f)

cases = []
for api in apis:
    for q in api["examples"]["positive"]:
        cases.append({
            "id": str(uuid.uuid4())[:2],
            "query": q,
            "expected_api": api["api"],
            "label": "positive"
        })
    for q in api["examples"]["negative"]:
        cases.append({
            "id": str(uuid.uuid4())[:2],
            "query": q,
            "expected_api": "other",
            "label": "negative"
        })

with open("testcases.json", "w", encoding="utf-8") as f:
    json.dump(cases, f, indent=2, ensure_ascii=False)

print(f"Generated {len(cases)} testcases for {len(apis)} APIs")
