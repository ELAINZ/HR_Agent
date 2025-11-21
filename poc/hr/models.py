"""
HR系统数据库模型
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Employee(db.Model):
    """员工信息表"""
    __tablename__ = 'employees'
    
    employee_id = db.Column(db.String(50), primary_key=True, comment='员工ID')
    name = db.Column(db.String(100), nullable=False, comment='姓名')
    department = db.Column(db.String(100), comment='部门')
    position = db.Column(db.String(100), comment='职位')
    join_date = db.Column(db.Date, comment='入职日期')
    address = db.Column(db.String(255), comment='地址')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    leaves = db.relationship('Leave', backref='employee', lazy=True)
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
    expenses = db.relationship('Expense', backref='employee', lazy=True)
    payrolls = db.relationship('Payroll', backref='employee', lazy=True)
    
    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'name': self.name,
            'department': self.department,
            'position': self.position,
            'join_date': self.join_date.strftime('%Y-%m-%d') if self.join_date else None,
            'address': self.address
        }


class LeaveBalance(db.Model):
    """请假余额表"""
    __tablename__ = 'leave_balances'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工ID')
    annual_leave_total = db.Column(db.Integer, default=10, comment='年假总额')
    annual_leave_used = db.Column(db.Integer, default=0, comment='年假已用')
    sick_leave_total = db.Column(db.Integer, default=5, comment='病假总额')
    sick_leave_used = db.Column(db.Integer, default=0, comment='病假已用')
    year = db.Column(db.Integer, default=lambda: datetime.now().year, comment='年份')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='leave_balance')
    
    @property
    def annual_leave_remaining(self):
        return self.annual_leave_total - self.annual_leave_used
    
    @property
    def sick_leave_remaining(self):
        return self.sick_leave_total - self.sick_leave_used
    
    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'annual_leave_total': self.annual_leave_total,
            'annual_leave_used': self.annual_leave_used,
            'annual_leave_remaining': self.annual_leave_remaining,
            'sick_leave_total': self.sick_leave_total,
            'sick_leave_used': self.sick_leave_used,
            'sick_leave_remaining': self.sick_leave_remaining,
            'year': self.year
        }


class Leave(db.Model):
    """请假申请表"""
    __tablename__ = 'leaves'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.String(50), unique=True, nullable=False, comment='申请ID')
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工ID')
    leave_type = db.Column(db.String(50), nullable=False, comment='请假类型：annual, sick, marriage, maternity等')
    start_date = db.Column(db.Date, nullable=False, comment='开始日期')
    end_date = db.Column(db.Date, nullable=False, comment='结束日期')
    days = db.Column(db.Integer, comment='请假天数')
    status = db.Column(db.String(20), default='submitted', comment='状态：submitted, approved, rejected')
    message = db.Column(db.Text, comment='备注信息')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        return {
            'application_id': self.application_id,
            'employee_id': self.employee_id,
            'leave_type': self.leave_type,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'days': self.days,
            'status': self.status,
            'message': self.message
        }


class Attendance(db.Model):
    """考勤表"""
    __tablename__ = 'attendances'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工ID')
    date = db.Column(db.Date, nullable=False, comment='日期')
    checkin_time = db.Column(db.Time, comment='签到时间')
    checkout_time = db.Column(db.Time, comment='签退时间')
    status = db.Column(db.String(20), default='出勤', comment='状态：出勤、迟到、早退、缺勤')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('employee_id', 'date', name='unique_employee_date'),)
    
    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'checkin_time': self.checkin_time.strftime('%H:%M') if self.checkin_time else None,
            'checkout_time': self.checkout_time.strftime('%H:%M') if self.checkout_time else None,
            'status': self.status
        }


class Expense(db.Model):
    """报销表"""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expense_id = db.Column(db.String(50), unique=True, nullable=False, comment='报销ID')
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工ID')
    amount = db.Column(db.Numeric(10, 2), nullable=False, comment='金额')
    category = db.Column(db.String(50), comment='类别：住宿、交通、餐饮等')
    voucher_id = db.Column(db.String(50), comment='凭证ID')
    status = db.Column(db.String(20), default='submitted', comment='状态：submitted, approved, rejected')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'expense_id': self.expense_id,
            'employee_id': self.employee_id,
            'amount': float(self.amount),
            'category': self.category,
            'voucher_id': self.voucher_id,
            'status': self.status
        }


class Payroll(db.Model):
    """薪酬表"""
    __tablename__ = 'payrolls'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工ID')
    month = db.Column(db.String(10), nullable=False, comment='月份，格式：YYYY-MM')
    salary = db.Column(db.Numeric(10, 2), comment='基本工资')
    tax = db.Column(db.Numeric(10, 2), default=0, comment='个人所得税')
    social_security = db.Column(db.Numeric(10, 2), default=0, comment='社保')
    status = db.Column(db.String(20), default='已发放', comment='状态')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('employee_id', 'month', name='unique_employee_month'),)
    
    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'month': self.month,
            'salary': float(self.salary) if self.salary else None,
            'tax': float(self.tax) if self.tax else None,
            'social_security': float(self.social_security) if self.social_security else None,
            'status': self.status
        }


class Travel(db.Model):
    """差旅申请表"""
    __tablename__ = 'travels'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    travel_id = db.Column(db.String(50), unique=True, nullable=False, comment='差旅ID')
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工ID')
    destination = db.Column(db.String(100), nullable=False, comment='目的地')
    start_date = db.Column(db.Date, nullable=False, comment='开始日期')
    end_date = db.Column(db.Date, nullable=False, comment='结束日期')
    status = db.Column(db.String(20), default='approved', comment='状态')
    message = db.Column(db.Text, comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'travel_id': self.travel_id,
            'employee_id': self.employee_id,
            'destination': self.destination,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
            'status': self.status,
            'message': self.message
        }


class Contract(db.Model):
    """合同表"""
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.String(50), db.ForeignKey('employees.employee_id'), nullable=False, comment='员工ID')
    contract_id = db.Column(db.String(50), unique=True, nullable=False, comment='合同ID')
    expire_date = db.Column(db.Date, comment='到期日期')
    renew_period = db.Column(db.String(50), comment='续约期限')
    status = db.Column(db.String(20), default='active', comment='状态：active, expired, renewed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'employee_id': self.employee_id,
            'contract_id': self.contract_id,
            'expire_date': self.expire_date.strftime('%Y-%m-%d') if self.expire_date else None,
            'renew_period': self.renew_period,
            'status': self.status
        }

