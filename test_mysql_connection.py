#!/usr/bin/env python3
"""测试 MySQL 数据库连接"""
from agent_platform.utils.config import Config
import pymysql

print("=" * 50)
print("测试 MySQL 数据库连接")
print("=" * 50)
print(f"主机: {Config.MYSQL_HOST}")
print(f"端口: {Config.MYSQL_PORT}")
print(f"用户: {Config.MYSQL_USER}")
print(f"数据库: {Config.MYSQL_DATABASE}")
print()

try:
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE
    )
    print("✓ MySQL 连接成功！")
    
    # 测试查询
    cursor = conn.cursor()
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"✓ MySQL 版本: {version[0]}")
    
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"✓ 数据库中的表数量: {len(tables)}")
    if tables:
        print("  表列表:")
        for table in tables:
            print(f"    - {table[0]}")
    
    cursor.close()
    conn.close()
    print("\n✓ 数据库连接测试通过！")
    
except pymysql.err.OperationalError as e:
    print(f"✗ MySQL 连接失败: {e}")
    print("\n可能的原因:")
    print("1. MySQL 容器未完全启动（等待 10-20 秒后重试）")
    print("2. IP 地址不正确")
    print("3. 端口被防火墙阻止")
    print("4. 数据库不存在，需要先创建")
    
    # 尝试创建数据库
    if "Unknown database" in str(e):
        print("\n尝试创建数据库...")
        try:
            conn = pymysql.connect(
                host=Config.MYSQL_HOST,
                port=Config.MYSQL_PORT,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            conn.commit()
            cursor.close()
            conn.close()
            print("✓ 数据库创建成功！")
        except Exception as e2:
            print(f"✗ 创建数据库失败: {e2}")
    
except Exception as e:
    print(f"✗ 发生错误: {e}")


