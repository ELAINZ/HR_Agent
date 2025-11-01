from fastapi import FastAPI, Query

app = FastAPI(title="HR Platform Mock API", description="模拟 HR Agent 测试 API 服务", version="1.0.0")

# ========== 请假相关 ==========
@app.get("/hr/leave/balance")
def leave_balance(employee_id: str = "E12345"):
    return {
        "employee_id": employee_id,
        "annual_leave_remaining": 7,
        "sick_leave_remaining": 2
    }

@app.post("/hr/leave/apply")
def leave_apply(employee_id: str = "E12345", leave_type: str = "annual", start_date: str = "2025-11-01", end_date: str = "2025-11-03"):
    return {
        "application_id": "APP001",
        "status": "submitted",
        "message": f"{employee_id} 申请 {leave_type} 假（{start_date} ~ {end_date}）成功"
    }

# ========== 政策相关 ==========
@app.get("/hr/policy")
def policy(topic: str = "婚假"):
    policies = {
        "婚假": "婚假3天，结婚证需提供复印件",
        "产假": "女员工产假98天",
        "丧假": "直系亲属丧假3天"
    }
    text = policies.get(topic, "暂无此政策")
    return {
        "topic": topic,
        "snippets": [{"text": f"{topic}政策说明：{text}", "source": "HR手册"}]
    }

# ========== 福利 ==========
@app.get("/hr/benefits/list")
def benefits_list(employee_id: str = "E12345"):
    return {
        "employee_id": employee_id,
        "benefits": ["餐补", "交通补贴", "节日礼金", "生日礼金"]
    }

@app.post("/hr/benefits/apply")
def benefits_apply(employee_id: str = "E12345", benefit_type: str = "生日礼金"):
    return {
        "application_id": "BEN001",
        "status": "approved",
        "message": f"{employee_id} 成功申请 {benefit_type}"
    }

# ========== 报销 / 差旅 ==========
@app.get("/hr/travel/policy")
def travel_policy(topic: str = "差旅标准"):
    return {
        "topic": topic,
        "snippets": [{"text": "经理以下经济舱，高管公务舱；酒店上限600元/晚", "source": "差旅制度"}]
    }

@app.post("/hr/travel/apply")
def travel_apply(employee_id: str = "E12345", destination: str = "上海", start_date: str = "2025-11-01", end_date: str = "2025-11-03"):
    return {
        "travel_id": "TRV001",
        "status": "approved",
        "message": f"{employee_id} 出差 {destination} 申请成功"
    }

@app.post("/hr/expense/submit")
def expense_submit(employee_id: str = "E12345", amount: int = 500, category: str = "住宿", voucher_id: str = "VC001"):
    return {
        "expense_id": "EXP001",
        "status": "submitted",
        "amount": amount,
        "category": category,
        "voucher_id": voucher_id
    }

# ========== 考勤 ==========
@app.post("/hr/attendance/checkin")
def attendance_checkin(employee_id: str = "E12345"):
    return {"employee_id": employee_id, "timestamp": "2025-10-30 09:00", "status": "checked_in"}

@app.get("/hr/attendance/status")
def attendance_status(employee_id: str = "E12345", date: str = "2025-10-30"):
    return {"employee_id": employee_id, "date": date, "status": "出勤", "checkin_time": "09:00"}

# ========== 工资薪酬 ==========
@app.get("/hr/payroll/info")
def payroll_info(employee_id: str = "E12345", month: str = "2025-09"):
    return {"employee_id": employee_id, "month": month, "salary": 15000, "status": "已发放"}

@app.get("/hr/payroll/tax")
def payroll_tax(employee_id: str = "E12345", month: str = "2025-09"):
    return {"employee_id": employee_id, "month": month, "tax": 1200, "social_security": 800}

# ========== 人事档案 ==========
@app.get("/hr/profile/view")
def profile_view(employee_id: str = "E12345"):
    return {
        "employee_id": employee_id,
        "name": "张三",
        "department": "技术部",
        "position": "后端工程师",
        "join_date": "2022-06-01"
    }

@app.post("/hr/profile/update")
def profile_update(employee_id: str = "E12345", field: str = "address", value: str = "上海市浦东新区"):
    return {"employee_id": employee_id, "updated_field": field, "new_value": value, "status": "success"}

# ========== 培训 ==========
@app.get("/hr/training/list")
def training_list(employee_id: str = "E12345"):
    return {"available_courses": ["领导力培训", "安全教育", "沟通技巧"]}

@app.post("/hr/training/apply")
def training_apply(employee_id: str = "E12345", course_id: str = "LD001"):
    return {"course_id": course_id, "status": "registered", "message": f"{employee_id} 报名课程 {course_id} 成功"}

# ========== 招聘 ==========
@app.get("/hr/recruitment/openings")
def recruitment_openings(department: str = "技术部"):
    return {"department": department, "positions": ["后端工程师", "测试工程师", "数据分析师"]}

@app.post("/hr/recruitment/referral")
def recruitment_referral(employee_id: str = "E12345", candidate_name: str = "李四"):
    return {"employee_id": employee_id, "candidate": candidate_name, "status": "推荐成功"}

# ========== 合同 ==========
@app.get("/hr/contract/view")
def contract_view(employee_id: str = "E12345"):
    return {"employee_id": employee_id, "contract_id": "CT001", "expire_date": "2025-12-31", "status": "active"}

@app.post("/hr/contract/renew")
def contract_renew(employee_id: str = "E12345", renew_period: str = "1年"):
    return {"employee_id": employee_id, "renew_period": renew_period, "status": "renewed"}

# ========== 运行入口 ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
