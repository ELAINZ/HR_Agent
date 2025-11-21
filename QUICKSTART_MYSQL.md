# MySQL 快速启动指南

## 快速开始（5分钟）

### 1. 安装 MySQL

确保 MySQL 已安装并运行：

```bash
# Windows (使用 MySQL Installer 或 XAMPP)
# 或使用 Docker
docker run --name mysql-hr -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=hr_agent -p 3306:3306 -d mysql:8.0

# Linux/Mac
sudo systemctl start mysql
# 或
brew services start mysql
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=hr_agent
```

### 3. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 4. 初始化数据库

```bash
python poc/hr/init_db.py
```

输出示例：
```
==================================================
HR系统数据库初始化
==================================================
数据库: hr_agent
主机: localhost:3306
==================================================
正在创建数据库表...
✓ 数据库表创建成功
正在插入初始数据...
✓ 初始数据插入成功
  - 员工: 2 条
  - 请假余额: 2 条
  - 薪酬记录: 2 条
  - 合同记录: 2 条

✓ 数据库初始化完成！
```

### 5. 启动服务器

```bash
python poc/hr/apis/flask_server.py
```

看到以下输出表示成功：
```
[数据库] 连接成功，表已创建/验证
 * Running on http://127.0.0.1:8000
```

### 6. 测试 API

```bash
# 健康检查
curl http://127.0.0.1:8000/health

# 查询请假余额
curl http://127.0.0.1:8000/hr/leave/balance?employee_id=E12345

# 申请请假
curl -X POST http://127.0.0.1:8000/hr/leave/apply \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"E12345","leave_type":"annual","start_date":"2025-11-01","end_date":"2025-11-03"}'
```

## 常见问题

### Q: 数据库连接失败怎么办？

A: 检查以下几点：
1. MySQL 服务是否运行：`mysql --version`
2. `.env` 文件配置是否正确
3. 数据库用户权限是否足够
4. 防火墙是否阻止连接

### Q: 表已存在错误？

A: 删除数据库重新创建：
```sql
DROP DATABASE hr_agent;
CREATE DATABASE hr_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

然后重新运行 `init_db.py`

### Q: 如何查看数据库中的数据？

A: 使用 MySQL 客户端：
```bash
mysql -u root -p hr_agent
```

然后执行 SQL：
```sql
SELECT * FROM employees;
SELECT * FROM leave_balances;
```

### Q: 数据库不可用时 API 还能用吗？

A: 可以！系统设计了容错机制，数据库不可用时会自动回退到默认数据模式，API 仍然可以正常工作。

## 下一步

- 查看 [MYSQL_SETUP.md](MYSQL_SETUP.md) 了解详细配置
- 查看 [FLASK_SETUP.md](FLASK_SETUP.md) 了解 Flask API 使用
- 根据需要修改数据库模型和业务逻辑

