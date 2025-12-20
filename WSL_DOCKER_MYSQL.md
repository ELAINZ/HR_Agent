# WSL 连接 Windows Docker MySQL 指南

## 问题说明

你的 MySQL 容器运行在 Windows 上的 Docker 中，端口映射为 `3307->3306`。

在 WSL 中连接时，需要：
1. 找到 Windows 主机的 IP 地址
2. 使用正确的端口（3307）

## 快速解决方案

### 方法一：在 WSL 中创建 .env 文件（推荐）

1. **获取 Windows 主机 IP**

在 WSL 中运行：
```bash
# 方法1：从 /etc/resolv.conf 获取
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'

# 方法2：使用 ip route
ip route show | grep -i default | awk '{ print $3}'

# 方法3：使用 hostname
hostname -I | awk '{print $1}'
```

通常 Windows 主机 IP 是类似 `172.x.x.x` 的地址。

2. **创建 .env 文件**

在项目根目录（`/mnt/d/Agent`）创建 `.env` 文件：

```bash
cd /mnt/d/Agent
nano .env
```

内容：
```env
# 使用 Windows 主机 IP 和 Docker 映射的端口
MYSQL_HOST=172.x.x.x  # 替换为上面获取的 IP
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=hr_agent
```

3. **测试连接**

```bash
# 测试 MySQL 连接
python3 -c "
from agent_platform.utils.config import Config
import pymysql
try:
    conn = pymysql.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD
    )
    print('✓ MySQL 连接成功！')
    conn.close()
except Exception as e:
    print(f'✗ MySQL 连接失败: {e}')
"
```

4. **初始化数据库**

```bash
python poc/hr/init_db.py
```

### 方法二：使用 localhost（如果 Docker Desktop 配置了端口转发）

如果 Docker Desktop 配置了 WSL 集成，可以直接使用 localhost：

```env
MYSQL_HOST=localhost
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=hr_agent
```

### 方法三：在 WSL 中启动 MySQL 容器

如果不想连接 Windows 的 Docker，可以在 WSL 中直接启动 MySQL：

```bash
# 停止 Windows 上的容器（可选）
# 在 Windows PowerShell 中：docker stop mysql8

# 在 WSL 中启动 MySQL 容器
docker run --name mysql-hr \
  -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=hr_agent \
  -p 3306:3306 \
  -d mysql:8.0

# 等待启动
sleep 10

# 验证
docker ps | grep mysql
```

然后使用标准配置：
```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=hr_agent
```

## 验证步骤

1. **检查容器状态**
   ```bash
   # 在 Windows PowerShell 中
   docker ps | findstr mysql
   ```

2. **检查端口映射**
   ```bash
   # 应该看到：0.0.0.0:3307->3306/tcp
   docker port mysql8
   ```

3. **测试连接（在 WSL 中）**
   ```bash
   # 使用获取的 Windows IP
   mysql -h 172.x.x.x -P 3307 -u root -proot -e "SHOW DATABASES;"
   ```

4. **创建数据库（如果不存在）**
   ```bash
   mysql -h 172.x.x.x -P 3307 -u root -proot -e "CREATE DATABASE IF NOT EXISTS hr_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```

5. **运行初始化脚本**
   ```bash
   python poc/hr/init_db.py
   ```

## 常见问题

### Q: 连接被拒绝 (Connection refused)

**原因**：
- Windows 防火墙阻止了端口
- IP 地址不正确
- 端口号错误

**解决**：
```bash
# 1. 检查 Windows 防火墙设置
# 在 Windows 中：控制面板 -> Windows Defender 防火墙 -> 允许应用通过防火墙

# 2. 验证 IP 和端口
ping <Windows_IP>
telnet <Windows_IP> 3307  # 如果安装了 telnet

# 3. 检查 Docker 端口映射
docker port mysql8
```

### Q: 找不到数据库

**解决**：
```bash
# 在 WSL 中创建数据库
mysql -h <Windows_IP> -P 3307 -u root -proot -e "CREATE DATABASE hr_agent CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### Q: 权限被拒绝

**解决**：
```bash
# 在 Windows Docker 容器中执行
docker exec -it mysql8 mysql -uroot -proot -e "GRANT ALL PRIVILEGES ON hr_agent.* TO 'root'@'%'; FLUSH PRIVILEGES;"
```

## 推荐配置

对于你的情况（MySQL 在 Windows Docker 中，端口 3307），推荐：

1. 在 WSL 中创建 `.env` 文件
2. 使用 Windows 主机 IP + 端口 3307
3. 确保 Windows 防火墙允许 3307 端口

示例 `.env`：
```env
MYSQL_HOST=172.20.144.1  # 替换为你的 Windows IP
MYSQL_PORT=3307
MYSQL_USER=root
MYSQL_PASSWORD=root
MYSQL_DATABASE=hr_agent
```

## 下一步

配置完成后：
1. ✅ 运行 `python poc/hr/init_db.py` 初始化数据库
2. ✅ 启动后端：`python poc/hr/apis/flask_server.py`
3. ✅ 启动前端：`cd frontend && npm run dev`

