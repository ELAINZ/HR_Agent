#!/bin/bash
# 使用 Docker 启动 MySQL 服务

echo "正在启动 MySQL Docker 容器..."

# 检查容器是否已存在
if docker ps -a | grep -q mysql-hr; then
    echo "MySQL 容器已存在，正在启动..."
    docker start mysql-hr
else
    echo "创建新的 MySQL 容器..."
    docker run --name mysql-hr \
      -e MYSQL_ROOT_PASSWORD=root \
      -e MYSQL_DATABASE=hr_agent \
      -p 3306:3306 \
      -d mysql:8.0
fi

# 等待 MySQL 启动
echo "等待 MySQL 启动..."
sleep 5

# 检查容器状态
if docker ps | grep -q mysql-hr; then
    echo "✓ MySQL 容器运行成功！"
    echo "连接信息："
    echo "  主机: localhost"
    echo "  端口: 3306"
    echo "  用户: root"
    echo "  密码: root"
    echo "  数据库: hr_agent"
else
    echo "✗ MySQL 容器启动失败"
    docker logs mysql-hr
fi


