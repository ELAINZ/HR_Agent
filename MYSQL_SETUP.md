# MySQL 数据库集成说明

## 概述

项目已成功集成 MySQL 数据库，使用 SQLAlchemy ORM 进行数据管理。所有 HR 相关的业务数据（员工、请假、考勤、薪酬等）都可以持久化存储。

## 数据库架构

### 主要数据表

1. **employees** - 员工信息表
2. **leave_balances** - 请假余额表
3. **leaves** - 请假申请表
4. **attendances** - 考勤表
5. **expenses** - 报销表
6. **payrolls** - 薪酬表
7. **travels** - 差旅申请表
8. **contracts** - 合同表

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置数据库连接

在项目根目录创建或编辑 `.env` 文件：

```env
# MySQL 数据库配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=hr_agent
```

### 3. 创建数据库

在 MySQL 中创建数据库：

```sql
CREATE DATABASE hr_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 初始化数据库

运行初始化脚本创建表结构和初始数据：

```bash
python poc/hr/init_db.py
```

这将：
- 创建所有数据库表
- 插入示例员工数据
- 创建示例请假余额、薪酬、合同记录

## 使用说明

### 启动服务器

```bash
python poc/hr/apis/flask_server.py
```

服务器启动时会自动：
- 连接 MySQL 数据库
- 如果表不存在，自动创建
- 如果数据库连接失败，会回退到默认数据模式（不影响 API 功能）

### API 使用示例

#### 查询请假余额（从数据库）

```bash
curl http://127.0.0.1:8000/hr/leave/balance?employee_id=E12345
```

响应：
```json
{
  "employee_id": "E12345",
  "annual_leave_total": 10,
  "annual_leave_used": 3,
  "annual_leave_remaining": 7,
  "sick_leave_total": 5,
  "sick_leave_used": 0,
  "sick_leave_remaining": 5,
  "year": 2025
}
```

#### 申请请假（保存到数据库）

```bash
curl -X POST http://127.0.0.1:8000/hr/leave/apply \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "E12345",
    "leave_type": "annual",
    "start_date": "2025-11-01",
    "end_date": "2025-11-03"
  }'
```

系统会自动：
- 创建请假申请记录
- 更新请假余额（如果是年假或病假）

#### 查询员工信息

```bash
curl http://127.0.0.1:8000/hr/profile/view?employee_id=E12345
```

#### 签到打卡

```bash
curl -X POST http://127.0.0.1:8000/hr/attendance/checkin \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "E12345"}'
```

## 数据库模型说明

### Employee（员工）
- `employee_id`: 员工ID（主键）
- `name`: 姓名
- `department`: 部门
- `position`: 职位
- `join_date`: 入职日期
- `address`: 地址

### LeaveBalance（请假余额）
- `employee_id`: 员工ID（外键）
- `annual_leave_total`: 年假总额
- `annual_leave_used`: 年假已用
- `sick_leave_total`: 病假总额
- `sick_leave_used`: 病假已用
- `year`: 年份

### Leave（请假申请）
- `application_id`: 申请ID（唯一）
- `employee_id`: 员工ID（外键）
- `leave_type`: 请假类型
- `start_date`: 开始日期
- `end_date`: 结束日期
- `days`: 请假天数
- `status`: 状态（submitted, approved, rejected）

### Attendance（考勤）
- `employee_id`: 员工ID（外键）
- `date`: 日期
- `checkin_time`: 签到时间
- `checkout_time`: 签退时间
- `status`: 状态

### Expense（报销）
- `expense_id`: 报销ID（唯一）
- `employee_id`: 员工ID（外键）
- `amount`: 金额
- `category`: 类别
- `voucher_id`: 凭证ID
- `status`: 状态

### Payroll（薪酬）
- `employee_id`: 员工ID（外键）
- `month`: 月份（YYYY-MM）
- `salary`: 基本工资
- `tax`: 个人所得税
- `social_security`: 社保
- `status`: 状态

### Travel（差旅）
- `travel_id`: 差旅ID（唯一）
- `employee_id`: 员工ID（外键）
- `destination`: 目的地
- `start_date`: 开始日期
- `end_date`: 结束日期
- `status`: 状态

### Contract（合同）
- `employee_id`: 员工ID（外键）
- `contract_id`: 合同ID（唯一）
- `expire_date`: 到期日期
- `renew_period`: 续约期限
- `status`: 状态

## 容错机制

系统设计了完善的容错机制：

1. **数据库连接失败**：如果 MySQL 连接失败，系统会自动回退到默认数据模式，API 仍然可以正常工作
2. **自动创建表**：首次运行时自动创建所有表结构
3. **自动创建员工**：查询不存在的员工时自动创建默认记录
4. **事务回滚**：操作失败时自动回滚，保证数据一致性

## 数据迁移

如果需要迁移现有数据：

1. 导出现有数据（如果有）
2. 运行 `init_db.py` 创建表结构
3. 使用 SQL 或 Python 脚本导入数据

## 注意事项

1. **字符集**：数据库使用 `utf8mb4` 字符集，支持中文和 emoji
2. **时区**：所有日期时间使用 UTC 存储，应用层转换为本地时间
3. **连接池**：配置了连接池，自动回收和重连
4. **索引**：建议为常用查询字段添加索引（如 employee_id, date 等）

## 健康检查

检查数据库连接状态：

```bash
curl http://127.0.0.1:8000/health
```

响应：
```json
{
  "status": "ok",
  "service": "HR Flask API",
  "database": "connected"
}
```

## 故障排查

### 问题：数据库连接失败

1. 检查 MySQL 服务是否运行
2. 检查 `.env` 文件配置是否正确
3. 检查数据库用户权限
4. 检查防火墙设置

### 问题：表创建失败

1. 检查数据库用户是否有 CREATE TABLE 权限
2. 检查数据库是否存在
3. 查看错误日志

### 问题：数据查询为空

1. 运行 `init_db.py` 初始化示例数据
2. 检查 employee_id 是否正确
3. 查看数据库表是否有数据

## 开发建议

1. **使用迁移工具**：生产环境建议使用 Flask-Migrate 进行数据库版本管理
2. **添加索引**：根据查询频率添加合适的索引
3. **数据备份**：定期备份数据库
4. **监控**：监控数据库连接数和查询性能

