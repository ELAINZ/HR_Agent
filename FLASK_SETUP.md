# Flask 后端集成说明

## 概述

项目已成功集成 Flask 后端，替代原有的 FastAPI 实现。所有 API 端点已完整迁移，保持与现有代码的兼容性。

## 文件说明

- **`poc/hr/apis/flask_server.py`**: Flask 版本的 API 服务器（完整实现）
- **`poc/hr/apis/server.py`**: 原有的 FastAPI 版本（保留，可选使用）
- **`poc/hr/apis/mock_hr_api.py`**: FastAPI Mock API（保留，可选使用）

## 安装依赖

```bash
# 激活虚拟环境（如果使用）
# Windows PowerShell:
.\myenv\Scripts\Activate.ps1
# Linux/Mac:
source myenv/bin/activate

# 安装 Flask 依赖
pip install -r requirements.txt
```

## 启动 Flask 服务器

### 方式一：直接运行
```bash
python poc/hr/apis/flask_server.py
```

### 方式二：使用启动脚本
```bash
# Windows
scripts\start_flask_api.bat

# Linux/Mac
bash scripts/start_flask_api.sh
```

服务器将在 `http://127.0.0.1:8000` 启动。

## API 端点

所有 API 端点与 FastAPI 版本保持一致：

### GET 请求示例
```bash
# 查询请假余额
curl http://127.0.0.1:8000/hr/leave/balance?employee_id=E12345

# 查询政策
curl http://127.0.0.1:8000/hr/policy?topic=婚假
```

### POST 请求示例
```bash
# 申请请假
curl -X POST http://127.0.0.1:8000/hr/leave/apply \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"E12345","leave_type":"annual","start_date":"2025-11-01","end_date":"2025-11-03"}'
```

## 主要变更

1. **请求参数获取方式**：
   - GET 请求：使用 `request.args.get()`
   - POST 请求：支持 JSON 和表单数据，使用 `request.get_json()` 或 `request.form.get()`

2. **响应格式**：
   - 使用 `jsonify()` 返回 JSON 响应

3. **跨域支持**：
   - 已集成 `flask-cors`，支持跨域请求

4. **RAG 集成**：
   - 保留了与 `TfidfRAG` 的集成，在 `/hr/policy` 和 `/hr/travel/policy` 端点中使用

## 兼容性

- ✅ 与现有的 `agent_platform/core/executor.py` 完全兼容
- ✅ 所有 API 端点路径保持不变
- ✅ 响应格式保持一致

## 健康检查

```bash
curl http://127.0.0.1:8000/health
```

## 注意事项

1. Flask 服务器默认运行在调试模式（`debug=True`），生产环境请修改为 `debug=False`
2. 如果 RAG 初始化失败，相关端点会回退到默认策略响应
3. 确保 `.env` 文件配置正确（如果使用环境变量）

