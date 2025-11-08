import os
from fastapi import FastAPI, Query
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from agent_platform.knowledge.retriever import TfidfRAG
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
rag = TfidfRAG()  # 读取本地索引

@app.get("/hr/leave/balance")
def leave_balance(employee_id: str = "E12345"):
    return {"employee_id": employee_id, "annual_leave_remaining": 7, "sick_leave_remaining": 2}

@app.post("/hr/leave/apply")
def leave_apply(employee_id: str = "E12345", leave_type: str = "annual", start_date: str = "", end_date: str = ""):
    return {"application_id": "APP001", "status": "submitted", "message": f"{employee_id}申请{leave_type}假成功"}

@app.get("/hr/policy")
def policy(topic: str = Query(default="")):
    # RAG 检索 返回片段与结构字段 便于稽核
    hits = rag.search(topic or "请假政策", k=3)
    return {
        "topic": topic,
        "snippets": hits,
        "source": "KB+RAG",
        "note": "结果来自本地知识库切片检索"
    }

@app.get("/hr/travel/policy")
def travel_policy(topic: str = Query(default="差旅标准")):
    hits = rag.search(topic, k=3)
    return {
        "topic": topic,
        "snippets": hits,
        "source": "KB+RAG"
    }

@app.post("/hr/expense/submit")
def expense_submit(employee_id: str = "E12345", amount: int = 500, category: str = "hotel", voucher_id: str = "V001"):
    return {"expense_id": "EXP001", "status": "submitted", "amount": amount, "category": category}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
