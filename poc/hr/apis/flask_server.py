import os
import sys
from datetime import datetime, date, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# 添加项目根目录到路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from agent_platform.knowledge.retriever import TfidfRAG
from agent_platform.utils.config import Config
from poc.hr.models import db, Employee, LeaveBalance, Leave, Attendance, Expense, Payroll, Travel, Contract
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 300,
    'pool_pre_ping': True
}

# 初始化数据库
db.init_app(app)

# 初始化RAG（如果需要）
try:
    rag = TfidfRAG()  # 读取本地索引
except Exception as e:
    print(f"警告: RAG初始化失败: {e}")
    rag = None

# 数据库连接状态
USE_DB = True
try:
    with app.app_context():
        db.create_all()  # 创建所有表
        print("[数据库] 连接成功，表已创建/验证")
except Exception as e:
    print(f"[数据库] 连接失败: {e}")
    print("[数据库] 将使用默认数据模式")
    USE_DB = False


def get_or_create_employee(employee_id: str):
    """获取或创建员工记录"""
    if not USE_DB:
        return None
    
    employee = Employee.query.filter_by(employee_id=employee_id).first()
    if not employee:
        employee = Employee(
            employee_id=employee_id,
            name="张三",
            department="技术部",
            position="后端工程师",
            join_date=date(2022, 6, 1)
        )
        db.session.add(employee)
        db.session.commit()
    return employee


# ========== 请假相关 ==========
@app.route("/hr/leave/balance", methods=["GET"])
def leave_balance():
    employee_id = request.args.get("employee_id", "E12345")
    
    if USE_DB:
        try:
            # 获取或创建员工
            employee = get_or_create_employee(employee_id)
            
            # 获取请假余额
            current_year = datetime.now().year
            balance = LeaveBalance.query.filter_by(
                employee_id=employee_id,
                year=current_year
            ).first()
            
            if not balance:
                # 创建默认余额
                balance = LeaveBalance(
                    employee_id=employee_id,
                    annual_leave_total=10,
                    annual_leave_used=0,
                    sick_leave_total=5,
                    sick_leave_used=0,
                    year=current_year
                )
                db.session.add(balance)
                db.session.commit()
            
            return jsonify(balance.to_dict())
        except Exception as e:
            print(f"[错误] 查询请假余额失败: {e}")
    
    # 回退到默认值
    return jsonify({
        "employee_id": employee_id,
        "annual_leave_remaining": 7,
        "sick_leave_remaining": 2
    })


@app.route("/hr/leave/apply", methods=["POST"])
def leave_apply():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    leave_type = data.get("leave_type", request.form.get("leave_type", "annual"))
    start_date_str = data.get("start_date", request.form.get("start_date", "2025-11-01"))
    end_date_str = data.get("end_date", request.form.get("end_date", "2025-11-03"))
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        days = (end_date - start_date).days + 1
    except:
        start_date = date(2025, 11, 1)
        end_date = date(2025, 11, 3)
        days = 3
    
    application_id = f"APP{uuid.uuid4().hex[:6].upper()}"
    
    if USE_DB:
        try:
            # 获取或创建员工
            employee = get_or_create_employee(employee_id)
            
            # 创建请假申请
            leave = Leave(
                application_id=application_id,
                employee_id=employee_id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                days=days,
                status="submitted",
                message=f"{employee_id} 申请 {leave_type} 假（{start_date_str} ~ {end_date_str}）成功"
            )
            db.session.add(leave)
            
            # 更新请假余额（如果是年假或病假）
            if leave_type in ['annual', 'sick']:
                current_year = datetime.now().year
                balance = LeaveBalance.query.filter_by(
                    employee_id=employee_id,
                    year=current_year
                ).first()
                
                if balance:
                    if leave_type == 'annual':
                        balance.annual_leave_used += days
                    elif leave_type == 'sick':
                        balance.sick_leave_used += days
            
            db.session.commit()
            
            return jsonify(leave.to_dict())
        except Exception as e:
            print(f"[错误] 申请请假失败: {e}")
            db.session.rollback()
    
    # 回退到默认响应
    return jsonify({
        "application_id": application_id,
        "status": "submitted",
        "message": f"{employee_id} 申请 {leave_type} 假（{start_date_str} ~ {end_date_str}）成功"
    })


# ========== 政策相关 ==========
@app.route("/hr/policy", methods=["GET"])
def policy():
    topic = request.args.get("topic", "婚假")
    
    # 如果RAG可用，使用RAG检索
    if rag:
        try:
            hits = rag.search(topic, k=3)
            return jsonify({
                "topic": topic,
                "snippets": hits,
                "source": "KB+RAG",
                "note": "结果来自本地知识库切片检索"
            })
        except Exception as e:
            print(f"RAG检索失败，使用默认策略: {e}")
    
    # 默认策略
    policies = {
        "婚假": "婚假3天，结婚证需提供复印件",
        "产假": "女员工产假98天",
        "丧假": "直系亲属丧假3天"
    }
    text = policies.get(topic, "暂无此政策")
    
    return jsonify({
        "topic": topic,
        "snippets": [{"text": f"{topic}政策说明：{text}", "source": "HR手册"}]
    })


# ========== 福利 ==========
@app.route("/hr/benefits/list", methods=["GET"])
def benefits_list():
    employee_id = request.args.get("employee_id", "E12345")
    return jsonify({
        "employee_id": employee_id,
        "benefits": ["餐补", "交通补贴", "节日礼金", "生日礼金"]
    })


@app.route("/hr/benefits/apply", methods=["POST"])
def benefits_apply():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    benefit_type = data.get("benefit_type", request.form.get("benefit_type", "生日礼金"))
    
    return jsonify({
        "application_id": "BEN001",
        "status": "approved",
        "message": f"{employee_id} 成功申请 {benefit_type}"
    })


# ========== 报销 / 差旅 ==========
@app.route("/hr/travel/policy", methods=["GET"])
def travel_policy():
    topic = request.args.get("topic", "差旅标准")
    
    # 如果RAG可用，使用RAG检索
    if rag:
        try:
            hits = rag.search(topic, k=3)
            return jsonify({
                "topic": topic,
                "snippets": hits,
                "source": "KB+RAG"
            })
        except Exception as e:
            print(f"RAG检索失败，使用默认策略: {e}")
    
    return jsonify({
        "topic": topic,
        "snippets": [{"text": "经理以下经济舱，高管公务舱；酒店上限600元/晚", "source": "差旅制度"}]
    })


@app.route("/hr/travel/apply", methods=["POST"])
def travel_apply():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    destination = data.get("destination", request.form.get("destination", "上海"))
    start_date_str = data.get("start_date", request.form.get("start_date", "2025-11-01"))
    end_date_str = data.get("end_date", request.form.get("end_date", "2025-11-03"))
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except:
        start_date = date(2025, 11, 1)
        end_date = date(2025, 11, 3)
    
    travel_id = f"TRV{uuid.uuid4().hex[:6].upper()}"
    
    if USE_DB:
        try:
            employee = get_or_create_employee(employee_id)
            
            travel = Travel(
                travel_id=travel_id,
                employee_id=employee_id,
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                status="approved",
                message=f"{employee_id} 出差 {destination} 申请成功"
            )
            db.session.add(travel)
            db.session.commit()
            
            return jsonify(travel.to_dict())
        except Exception as e:
            print(f"[错误] 申请差旅失败: {e}")
            db.session.rollback()
    
    return jsonify({
        "travel_id": travel_id,
        "status": "approved",
        "message": f"{employee_id} 出差 {destination} 申请成功"
    })


@app.route("/hr/expense/submit", methods=["POST"])
def expense_submit():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    amount = float(data.get("amount", request.form.get("amount", 500)))
    category = data.get("category", request.form.get("category", "住宿"))
    voucher_id = data.get("voucher_id", request.form.get("voucher_id", "VC001"))
    
    expense_id = f"EXP{uuid.uuid4().hex[:6].upper()}"
    
    if USE_DB:
        try:
            employee = get_or_create_employee(employee_id)
            
            expense = Expense(
                expense_id=expense_id,
                employee_id=employee_id,
                amount=amount,
                category=category,
                voucher_id=voucher_id,
                status="submitted"
            )
            db.session.add(expense)
            db.session.commit()
            
            return jsonify(expense.to_dict())
        except Exception as e:
            print(f"[错误] 提交报销失败: {e}")
            db.session.rollback()
    
    return jsonify({
        "expense_id": expense_id,
        "status": "submitted",
        "amount": amount,
        "category": category,
        "voucher_id": voucher_id
    })


# ========== 考勤 ==========
@app.route("/hr/attendance/checkin", methods=["POST"])
def attendance_checkin():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    
    today = date.today()
    current_time = datetime.now().time()
    
    if USE_DB:
        try:
            employee = get_or_create_employee(employee_id)
            
            # 检查今天是否已签到
            attendance = Attendance.query.filter_by(
                employee_id=employee_id,
                date=today
            ).first()
            
            if attendance:
                attendance.checkin_time = current_time
                attendance.status = "出勤"
            else:
                attendance = Attendance(
                    employee_id=employee_id,
                    date=today,
                    checkin_time=current_time,
                    status="出勤"
                )
                db.session.add(attendance)
            
            db.session.commit()
            
            return jsonify({
                "employee_id": employee_id,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "checked_in"
            })
        except Exception as e:
            print(f"[错误] 签到失败: {e}")
            db.session.rollback()
    
    return jsonify({
        "employee_id": employee_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "checked_in"
    })


@app.route("/hr/attendance/status", methods=["GET"])
def attendance_status():
    employee_id = request.args.get("employee_id", "E12345")
    date_str = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    
    try:
        query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        query_date = date.today()
    
    if USE_DB:
        try:
            attendance = Attendance.query.filter_by(
                employee_id=employee_id,
                date=query_date
            ).first()
            
            if attendance:
                return jsonify(attendance.to_dict())
        except Exception as e:
            print(f"[错误] 查询考勤失败: {e}")
    
    return jsonify({
        "employee_id": employee_id,
        "date": date_str,
        "status": "出勤",
        "checkin_time": "09:00"
    })


# ========== 工资薪酬 ==========
@app.route("/hr/payroll/info", methods=["GET"])
def payroll_info():
    employee_id = request.args.get("employee_id", "E12345")
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    
    if USE_DB:
        try:
            payroll = Payroll.query.filter_by(
                employee_id=employee_id,
                month=month
            ).first()
            
            if payroll:
                return jsonify(payroll.to_dict())
            else:
                # 创建默认薪酬记录
                payroll = Payroll(
                    employee_id=employee_id,
                    month=month,
                    salary=15000,
                    status="已发放"
                )
                db.session.add(payroll)
                db.session.commit()
                return jsonify(payroll.to_dict())
        except Exception as e:
            print(f"[错误] 查询薪酬失败: {e}")
            db.session.rollback()
    
    return jsonify({
        "employee_id": employee_id,
        "month": month,
        "salary": 15000,
        "status": "已发放"
    })


@app.route("/hr/payroll/tax", methods=["GET"])
def payroll_tax():
    employee_id = request.args.get("employee_id", "E12345")
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))
    
    if USE_DB:
        try:
            payroll = Payroll.query.filter_by(
                employee_id=employee_id,
                month=month
            ).first()
            
            if payroll:
                return jsonify({
                    "employee_id": employee_id,
                    "month": month,
                    "tax": float(payroll.tax) if payroll.tax else 1200,
                    "social_security": float(payroll.social_security) if payroll.social_security else 800
                })
        except Exception as e:
            print(f"[错误] 查询税费失败: {e}")
    
    return jsonify({
        "employee_id": employee_id,
        "month": month,
        "tax": 1200,
        "social_security": 800
    })


# ========== 人事档案 ==========
@app.route("/hr/profile/view", methods=["GET"])
def profile_view():
    employee_id = request.args.get("employee_id", "E12345")
    
    if USE_DB:
        try:
            employee = Employee.query.filter_by(employee_id=employee_id).first()
            if employee:
                return jsonify(employee.to_dict())
        except Exception as e:
            print(f"[错误] 查询员工信息失败: {e}")
    
    return jsonify({
        "employee_id": employee_id,
        "name": "张三",
        "department": "技术部",
        "position": "后端工程师",
        "join_date": "2022-06-01"
    })


@app.route("/hr/profile/update", methods=["POST"])
def profile_update():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    field = data.get("field", request.form.get("field", "address"))
    value = data.get("value", request.form.get("value", "上海市浦东新区"))
    
    if USE_DB:
        try:
            employee = get_or_create_employee(employee_id)
            
            if hasattr(employee, field):
                setattr(employee, field, value)
                db.session.commit()
                return jsonify({
                    "employee_id": employee_id,
                    "updated_field": field,
                    "new_value": value,
                    "status": "success"
                })
        except Exception as e:
            print(f"[错误] 更新员工信息失败: {e}")
            db.session.rollback()
    
    return jsonify({
        "employee_id": employee_id,
        "updated_field": field,
        "new_value": value,
        "status": "success"
    })


# ========== 培训 ==========
@app.route("/hr/training/list", methods=["GET"])
def training_list():
    employee_id = request.args.get("employee_id", "E12345")
    return jsonify({
        "available_courses": ["领导力培训", "安全教育", "沟通技巧"]
    })


@app.route("/hr/training/apply", methods=["POST"])
def training_apply():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    course_id = data.get("course_id", request.form.get("course_id", "LD001"))
    
    return jsonify({
        "course_id": course_id,
        "status": "registered",
        "message": f"{employee_id} 报名课程 {course_id} 成功"
    })


# ========== 招聘 ==========
@app.route("/hr/recruitment/openings", methods=["GET"])
def recruitment_openings():
    department = request.args.get("department", "技术部")
    return jsonify({
        "department": department,
        "positions": ["后端工程师", "测试工程师", "数据分析师"]
    })


@app.route("/hr/recruitment/referral", methods=["POST"])
def recruitment_referral():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    candidate_name = data.get("candidate_name", request.form.get("candidate_name", "李四"))
    
    return jsonify({
        "employee_id": employee_id,
        "candidate": candidate_name,
        "status": "推荐成功"
    })


# ========== 合同 ==========
@app.route("/hr/contract/view", methods=["GET"])
def contract_view():
    employee_id = request.args.get("employee_id", "E12345")
    
    if USE_DB:
        try:
            contract = Contract.query.filter_by(employee_id=employee_id).first()
            if contract:
                return jsonify(contract.to_dict())
            else:
                # 创建默认合同
                contract = Contract(
                    employee_id=employee_id,
                    contract_id=f"CT{uuid.uuid4().hex[:6].upper()}",
                    expire_date=date(2025, 12, 31),
                    status="active"
                )
                db.session.add(contract)
                db.session.commit()
                return jsonify(contract.to_dict())
        except Exception as e:
            print(f"[错误] 查询合同失败: {e}")
            db.session.rollback()
    
    return jsonify({
        "employee_id": employee_id,
        "contract_id": "CT001",
        "expire_date": "2025-12-31",
        "status": "active"
    })


@app.route("/hr/contract/renew", methods=["POST"])
def contract_renew():
    data = request.get_json() if request.is_json else {}
    employee_id = data.get("employee_id", request.form.get("employee_id", "E12345"))
    renew_period = data.get("renew_period", request.form.get("renew_period", "1年"))
    
    if USE_DB:
        try:
            contract = Contract.query.filter_by(employee_id=employee_id).first()
            if contract:
                contract.renew_period = renew_period
                contract.status = "renewed"
                # 根据续约期限更新到期日期
                if "年" in renew_period:
                    years = int(renew_period.replace("年", ""))
                    contract.expire_date = date.today() + timedelta(days=years * 365)
                db.session.commit()
                return jsonify(contract.to_dict())
        except Exception as e:
            print(f"[错误] 续约合同失败: {e}")
            db.session.rollback()
    
    return jsonify({
        "employee_id": employee_id,
        "renew_period": renew_period,
        "status": "renewed"
    })


# ========== 健康检查 ==========
@app.route("/health", methods=["GET"])
def health():
    db_status = "connected" if USE_DB else "disconnected"
    return jsonify({
        "status": "ok",
        "service": "HR Flask API",
        "database": db_status
    })


# ========== 运行入口 ==========
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
