"""
数据库初始化脚本
用于创建数据库表和插入初始数据
"""
import os
import sys
from datetime import date

# 添加项目根目录到路径（确保在开头，优先级最高）
# init_db.py 位于 poc/hr/，需要向上两级到达项目根目录
_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.normpath(os.path.join(_script_dir, "../.."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# 调试信息（可通过环境变量启用）
if os.getenv("DEBUG", "").lower() in ("1", "true", "yes"):
    print(f"[DEBUG] 脚本目录: {_script_dir}")
    print(f"[DEBUG] 项目根目录: {_project_root}")
    print(f"[DEBUG] agent_platform 路径: {os.path.join(_project_root, 'agent_platform')}")
    print(f"[DEBUG] agent_platform 存在: {os.path.exists(os.path.join(_project_root, 'agent_platform'))}")

try:
    from flask import Flask
    from agent_platform.utils.config import Config
    from poc.hr.models import (
        db, Employee, LeaveBalance, Payroll, Contract,
        Leave, Attendance, Expense, Travel
    )
except ImportError as e:
    print(f"[错误] 模块导入失败: {e}")
    print(f"[错误] 当前工作目录: {os.getcwd()}")
    print(f"[错误] 脚本文件: {__file__}")
    print(f"[错误] 脚本目录: {_script_dir}")
    print(f"[错误] 项目根目录: {_project_root}")
    print(f"[错误] agent_platform 存在: {os.path.exists(os.path.join(_project_root, 'agent_platform'))}")
    print(f"[错误] 请确保在项目根目录运行此脚本，或检查 Python 路径配置")
    raise
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
config = Config()
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def init_database():
    """初始化数据库"""
    with app.app_context():
        try:
            # 创建所有表
            print("正在创建数据库表...")
            db.create_all()
            print("✓ 数据库表创建成功")
            
            # 检查是否已有数据
            if Employee.query.first():
                print("检测到数据库已有数据")
                response = input("是否清空现有数据并重新初始化？(y/N): ").strip().lower()
                if response == 'y':
                    print("正在清空现有数据...")
                    # 按依赖关系顺序删除
                    db.session.query(Contract).delete()
                    db.session.query(Payroll).delete()
                    db.session.query(LeaveBalance).delete()
                    db.session.query(Leave).delete()
                    db.session.query(Attendance).delete()
                    db.session.query(Expense).delete()
                    db.session.query(Travel).delete()
                    db.session.query(Employee).delete()
                    db.session.commit()
                    print("✓ 数据已清空")
                else:
                    print("跳过初始化数据")
                    return
            
            # 插入示例数据
            print("正在插入初始数据...")
            
            # 创建示例员工
            employees = [
                Employee(
                    employee_id="E12345",
                    name="张三",
                    department="技术部",
                    position="后端工程师",
                    join_date=date(2022, 6, 1),
                    address="上海市浦东新区"
                ),
                Employee(
                    employee_id="E12346",
                    name="李四",
                    department="产品部",
                    position="产品经理",
                    join_date=date(2023, 3, 15),
                    address="北京市朝阳区"
                ),
            ]
            
            # 先提交员工数据，确保外键约束满足
            for emp in employees:
                db.session.add(emp)
            db.session.commit()
            print("  - 员工数据已提交")
            
            # 创建请假余额
            current_year = date.today().year
            leave_balances = [
                LeaveBalance(
                    employee_id="E12345",
                    annual_leave_total=30,  # 默认年假 30 天
                    annual_leave_used=3,
                    sick_leave_total=30,  # 默认病假 30 天
                    sick_leave_used=0,
                    year=current_year
                ),
                LeaveBalance(
                    employee_id="E12346",
                    annual_leave_total=30,  # 默认年假 30 天
                    annual_leave_used=0,
                    sick_leave_total=30,  # 默认病假 30 天
                    sick_leave_used=1,
                    year=current_year
                ),
            ]
            
            for balance in leave_balances:
                db.session.add(balance)
            db.session.commit()
            print("  - 请假余额数据已提交")
            
            # 创建薪酬记录
            payrolls = [
                Payroll(
                    employee_id="E12345",
                    month="2025-09",
                    salary=15000,
                    tax=1200,
                    social_security=800,
                    status="已发放"
                ),
                Payroll(
                    employee_id="E12346",
                    month="2025-09",
                    salary=18000,
                    tax=1500,
                    social_security=1000,
                    status="已发放"
                ),
            ]
            
            for payroll in payrolls:
                db.session.add(payroll)
            db.session.commit()
            print("  - 薪酬数据已提交")
            
            # 创建合同记录
            contracts = [
                Contract(
                    employee_id="E12345",
                    contract_id="CT001",
                    expire_date=date(2025, 12, 31),
                    status="active"
                ),
                Contract(
                    employee_id="E12346",
                    contract_id="CT002",
                    expire_date=date(2026, 6, 30),
                    status="active"
                ),
            ]
            
            for contract in contracts:
                db.session.add(contract)
            db.session.commit()
            print("  - 合同数据已提交")
            print("✓ 初始数据插入成功")
            print(f"  - 员工: {len(employees)} 条")
            print(f"  - 请假余额: {len(leave_balances)} 条")
            print(f"  - 薪酬记录: {len(payrolls)} 条")
            print(f"  - 合同记录: {len(contracts)} 条")
            
        except Exception as e:
            print(f"✗ 数据库初始化失败: {e}")
            db.session.rollback()
            raise


if __name__ == "__main__":
    print("=" * 50)
    print("HR系统数据库初始化")
    print("=" * 50)
    print(f"数据库: {Config.MYSQL_DATABASE}")
    print(f"主机: {Config.MYSQL_HOST}:{Config.MYSQL_PORT}")
    print("=" * 50)
    
    try:
        init_database()
        print("\n✓ 数据库初始化完成！")
    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        sys.exit(1)

