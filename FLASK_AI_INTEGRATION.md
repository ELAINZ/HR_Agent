# Flask 与 AI 集成架构说明

## 📋 概述

本文档详细说明 Flask 后端服务器如何与 AI 组件（LLM 路由、评估器等）集成工作。

## 🔗 核心集成流程

### 1. Flask 作为 HTTP API 服务器

Flask 服务器 (`poc/hr/apis/flask_server.py`) 提供两类 API：

#### A. 业务 API（HR 功能）
- `/hr/leave/balance` - 查询请假余额
- `/hr/leave/apply` - 申请请假
- `/hr/attendance/checkin` - 打卡签到
- `/hr/payroll/info` - 查询工资
- ... 等等

#### B. 评估 API（AI 测试）
- `/eval/llm/route` - LLM 路由测试
- `/eval/run` - 基础评估
- `/eval/comprehensive` - 综合评估
- `/eval/testcases` - 获取测试用例

---

## 🤖 AI 组件架构

### 组件层次结构

```
Flask Server (poc/hr/apis/flask_server.py)
    │
    ├─→ LLMRouter (agent_platform/router/llm_router.py)
    │   └─→ Moonshot API (LLM 模型)
    │
    ├─→ Executor (agent_platform/core/executor.py)
    │   └─→ HTTP 请求 → Flask API 端点
    │
    ├─→ Evaluator (agent_platform/core/evaluator.py)
    │   └─→ Moonshot API (错误分析)
    │
    └─→ DeepEval Metrics (agent_platform/core/deepeval_metrics.py)
        ├─→ RouterAccuracyMetric
        ├─→ JSONResponseMetric
        └─→ HallucinationRuleMetric
```

---

## 🔄 数据流详解

### 场景 1: LLM 路由测试 (`/eval/llm/route`)

```python
# Flask 路由处理
@app.route("/eval/llm/route", methods=["POST"])
def llm_route_test():
    query = request.json.get("query")
    
    # 1. 导入并初始化 LLMRouter
    from agent_platform.router.llm_router import LLMRouter
    router = LLMRouter()
    
    # 2. 调用 AI 路由规划
    predicted_api = router.plan(query)
    #    ↓
    #    router.plan() 内部：
    #    - 构造 prompt（包含所有可用 API）
    #    - 调用 Moonshot API (OpenAI SDK)
    #    - 返回预测的 API 路径
    
    # 3. 返回结果
    return jsonify({
        "query": query,
        "predicted_api": predicted_api,
        "status": "success"
    })
```

**流程图：**
```
HTTP POST /eval/llm/route
    ↓
Flask 接收请求
    ↓
创建 LLMRouter 实例
    ↓
router.plan(query)
    ↓
调用 Moonshot API (LLM)
    ↓
返回预测的 API 路径
    ↓
Flask 返回 JSON 响应
```

---

### 场景 2: 基础评估 (`/eval/run`)

```python
@app.route("/eval/run", methods=["POST"])
def run_evaluation():
    # 1. 初始化所有 AI 组件
    router = LLMRouter()      # AI 路由规划器
    executor = Executor()      # API 执行器
    evaluator = Evaluator()   # 评估器
    
    # 2. 加载测试用例
    cases = load_testcases()
    
    # 3. 对每个测试用例：
    for case in cases:
        # 3.1 AI 路由预测
        predicted_api = router.plan(case["query"])
        
        # 3.2 评估路由准确性
        eval_result = evaluator.evaluate(case, predicted_api)
        #    ↓
        #    evaluator.evaluate() 内部：
        #    - 比较 predicted_api 和 expected_api
        #    - 如果错误，调用 LLM 生成错误原因
        #    - 返回评估结果
        
        results.append(eval_result)
    
    # 4. 返回评估结果
    return jsonify({
        "results": results,
        "total": len(results),
        "passed": passed_count,
        "failed": failed_count,
        "accuracy": accuracy_percentage
    })
```

**流程图：**
```
HTTP POST /eval/run
    ↓
Flask 初始化 AI 组件
    ↓
加载测试用例
    ↓
┌─────────────────────────┐
│ 对每个测试用例循环：      │
│                          │
│  1. router.plan()        │ ← 调用 Moonshot API
│     ↓                    │
│  2. evaluator.evaluate() │ ← 可能调用 Moonshot API（错误分析）
│     ↓                    │
│  3. 收集结果              │
└─────────────────────────┘
    ↓
返回评估报告
```

---

### 场景 3: 综合评估 (`/eval/comprehensive`)

这是最完整的评估流程，包含路由、JSON 质量、幻觉检测：

```python
@app.route("/eval/comprehensive", methods=["POST"])
def run_comprehensive_evaluation():
    # 1. 初始化组件
    router = LLMRouter()
    executor = Executor()      # 执行器会调用 Flask API
    evaluator = Evaluator()
    
    # 2. 对每个测试用例：
    for case in cases:
        # 2.1 AI 路由预测
        predicted_api = router.plan(case["query"])
        
        # 2.2 执行 API 调用（Executor 调用 Flask 的业务 API）
        resp, latency = executor.execute(
            case_id=case["id"],
            query=case["query"],
            route_plan=predicted_api
        )
        #    ↓
        #    executor.execute() 内部：
        #    - 构造 URL: http://127.0.0.1:8000{predicted_api}
        #    - 发送 HTTP GET 请求
        #    - 调用 Flask 的业务 API（如 /hr/leave/balance）
        #    - 记录日志到 Langfuse
        #    - 返回响应数据
        
        # 2.3 路由准确性评估
        eval_result = evaluator.evaluate(case, predicted_api)
        
        # 2.4 JSON 结构质量评估
        json_metric = JSONResponseMetric()
        json_score = json_metric.measure(test_case)
        
        # 2.5 幻觉检测
        hallucination_metric = HallucinationRuleMetric()
        hallucination_score = hallucination_metric.measure(test_case)
        
        results.append({
            **eval_result,
            "json_score": json_score,
            "hallucination_score": hallucination_score,
            "response": resp
        })
    
    return jsonify({
        "results": results,
        "accuracy": ...,
        "json_quality": ...,
        "hallucination_rate": ...
    })
```

**完整流程图：**
```
HTTP POST /eval/comprehensive
    ↓
Flask 初始化 AI 组件
    ↓
加载测试用例和响应规范
    ↓
┌─────────────────────────────────────┐
│ 对每个测试用例循环：                  │
│                                      │
│  1. router.plan(query)               │ ← Moonshot API
│     ↓                                │
│  2. executor.execute(route_plan)     │
│     ↓                                │
│     HTTP GET → Flask 业务 API         │ ← 调用 Flask 自己的端点
│     ↓                                │
│     返回业务数据                      │
│     ↓                                │
│  3. evaluator.evaluate()             │ ← Moonshot API（错误分析）
│     ↓                                │
│  4. JSONResponseMetric.measure()     │ ← JSON 结构检查
│     ↓                                │
│  5. HallucinationRuleMetric.measure()│ ← 幻觉检测
│     ↓                                │
│  6. 收集所有评估结果                  │
└─────────────────────────────────────┘
    ↓
返回综合评估报告
```

---

## 🔍 关键组件详解

### 1. LLMRouter (`agent_platform/router/llm_router.py`)

**功能：** 使用 LLM 将用户查询路由到正确的 API

**工作方式：**
```python
class LLMRouter:
    def __init__(self):
        # 初始化 OpenAI SDK，指向 Moonshot API
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.moonshot.cn/v1"
        )
        # 加载 API 注册表
        self.apis = load_api_registry()
    
    def plan(self, query: str) -> str:
        # 构造 prompt，包含所有可用 API
        prompt = f"""
        你是一个智能HR系统的路由规划器。
        可用API：
        {format_apis(self.apis)}
        
        用户问题：{query}
        
        输出API路径：/hr/leave/balance
        """
        
        # 调用 Moonshot API
        response = self.client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[
                {"role": "system", "content": "你是一个精确的 API 分类助手。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        
        # 提取并清理返回的 API 路径
        return clean_api_path(response.choices[0].message.content)
```

**与 Flask 的关系：**
- Flask 在评估端点中导入并调用 `LLMRouter`
- `LLMRouter` 不直接调用 Flask，而是调用外部 LLM API（Moonshot）

---

### 2. Executor (`agent_platform/core/executor.py`)

**功能：** 执行 API 调用并记录日志

**工作方式：**
```python
class Executor:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url  # Flask 服务器地址
        self.langfuse = LangfuseClient()
    
    def execute(self, case_id, query, route_plan):
        # 构造完整的 URL
        url = f"{self.base_url}{route_plan}"
        # 例如: http://127.0.0.1:8000/hr/leave/balance
        
        # 发送 HTTP 请求到 Flask 服务器
        resp = requests.get(url).json()
        
        # 记录日志到 Langfuse
        trace = self.langfuse.trace_start(...)
        self.langfuse.log(trace, "api_call", {"url": url, "response": resp})
        
        return resp, latency
```

**与 Flask 的关系：**
- `Executor` **直接调用 Flask 的业务 API**
- 这是一个**循环调用**：Flask 评估端点 → Executor → Flask 业务端点
- 例如：`/eval/comprehensive` → `Executor.execute()` → `/hr/leave/balance`

---

### 3. Evaluator (`agent_platform/core/evaluator.py`)

**功能：** 评估路由准确性，使用 LLM 生成错误分析

**工作方式：**
```python
class Evaluator:
    def __init__(self):
        # 初始化 Moonshot API 客户端
        self.client = OpenAI(
            api_key=os.getenv("MOONSHOT_API_KEY"),
            base_url="https://api.moonshot.cn/v1"
        )
    
    def evaluate(self, case, predicted_api):
        expected = case["expected_api"]
        passed = (predicted_api == expected)
        
        if not passed:
            # 调用 LLM 生成错误原因
            error_reason = self._analyze_error(
                case["query"], 
                expected, 
                predicted_api
            )
            #    ↓
            #    _analyze_error() 内部调用 Moonshot API
            #    生成自然语言错误分析
        
        return {
            "pass": passed,
            "error": error_reason,
            ...
        }
```

**与 Flask 的关系：**
- Flask 在评估端点中导入并调用 `Evaluator`
- `Evaluator` 调用外部 LLM API（Moonshot）进行错误分析
- 不直接调用 Flask

---

### 4. DeepEval Metrics (`agent_platform/core/deepeval_metrics.py`)

**功能：** 使用 DeepEval 框架进行质量评估

**包含的指标：**
- `RouterAccuracyMetric` - 路由准确性
- `JSONResponseMetric` - JSON 响应结构质量
- `HallucinationRuleMetric` - 幻觉检测（检测 AI 是否生成虚假信息）

**与 Flask 的关系：**
- Flask 在综合评估中导入并使用这些指标
- 这些指标评估 Flask API 返回的数据质量

---

## 🔄 完整调用链示例

### 示例：综合评估一个测试用例

```
1. 用户发送请求
   POST http://127.0.0.1:8000/eval/comprehensive
   Body: {"type": "single", "query": "我今年年假还剩几天？"}

2. Flask 接收请求
   flask_server.py: run_comprehensive_evaluation()

3. Flask 初始化 AI 组件
   router = LLMRouter()
   executor = Executor(base_url="http://127.0.0.1:8000")
   evaluator = Evaluator()

4. AI 路由预测
   router.plan("我今年年假还剩几天？")
   ↓
   调用 Moonshot API
   ↓
   返回: "/hr/leave/balance"

5. 执行 API 调用
   executor.execute(
       case_id="test",
       query="我今年年假还剩几天？",
       route_plan="/hr/leave/balance"
   )
   ↓
   发送 HTTP GET http://127.0.0.1:8000/hr/leave/balance
   ↓
   Flask 业务端点处理请求
   ↓
   返回: {"annual_leave": 10, "sick_leave": 5, ...}

6. 路由准确性评估
   evaluator.evaluate(case, "/hr/leave/balance")
   ↓
   如果错误，调用 Moonshot API 生成错误原因
   ↓
   返回: {"pass": True, ...}

7. JSON 质量评估
   JSONResponseMetric.measure(test_case)
   ↓
   检查响应结构是否符合规范

8. 幻觉检测
   HallucinationRuleMetric.measure(test_case)
   ↓
   检查响应是否包含虚假信息

9. Flask 返回综合评估结果
   {
     "results": [{
       "pass": True,
       "json_score": 0.95,
       "hallucination_score": 1.0,
       "response": {...}
     }],
     "accuracy": 100,
     "json_quality": 95,
     "hallucination_rate": 100
   }
```

---

## 📊 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Flask Server                            │
│              (poc/hr/apis/flask_server.py)                 │
│                    Port: 8000                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │   业务 API       │      │   评估 API       │            │
│  │                  │      │                  │            │
│  │ /hr/leave/balance│      │ /eval/llm/route  │            │
│  │ /hr/leave/apply  │      │ /eval/run        │            │
│  │ /hr/payroll/info │      │ /eval/comprehensive│          │
│  │ ...              │      │ ...              │            │
│  └──────────────────┘      └──────────────────┘            │
│         ↑                           │                      │
│         │                           │                      │
│         │                           │ 导入并调用           │
│         │                           ↓                      │
│         │              ┌──────────────────────────┐        │
│         │              │   AI 组件层               │        │
│         │              │                          │        │
│         │              │  ┌────────────────────┐  │        │
│         │              │  │  LLMRouter         │  │        │
│         │              │  │  (路由规划)        │  │        │
│         │              │  └────────────────────┘  │        │
│         │              │           │              │        │
│         │              │  ┌────────────────────┐  │        │
│         │              │  │  Executor          │  │        │
│         │              │  │  (API 执行器)       │  │        │
│         │              │  └────────────────────┘  │        │
│         │              │           │              │        │
│         │              │  ┌────────────────────┐  │        │
│         │              │  │  Evaluator         │  │        │
│         │              │  │  (评估器)          │  │        │
│         │              │  └────────────────────┘  │        │
│         │              │           │              │        │
│         │              │  ┌────────────────────┐  │        │
│         │              │  │  DeepEval Metrics  │  │        │
│         │              │  │  (质量指标)        │  │        │
│         │              │  └────────────────────┘  │        │
│         │              └──────────────────────────┘        │
│         │                           │                      │
│         │                           │                      │
│         └───────────────────────────┘                      │
│                    (Executor 调用业务 API)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP 请求
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ↓                                       ↓
┌───────────────┐                      ┌───────────────┐
│  Moonshot API │                      │  Langfuse     │
│  (LLM 模型)   │                      │  (日志追踪)   │
│               │                      │               │
│ - 路由预测    │                      │ - 调用日志    │
│ - 错误分析    │                      │ - 性能指标    │
└───────────────┘                      └───────────────┘
```

---

## 🔑 关键点总结

1. **Flask 是中心服务器**
   - 提供业务 API 和评估 API
   - 评估 API 导入并使用 AI 组件

2. **AI 组件是独立的 Python 类**
   - `LLMRouter` - 调用外部 LLM API（Moonshot）
   - `Evaluator` - 调用外部 LLM API（Moonshot）
   - `Executor` - 调用 Flask 自己的业务 API（循环调用）
   - `DeepEval Metrics` - 评估数据质量

3. **调用关系**
   - Flask → AI 组件（导入并调用）
   - AI 组件 → 外部服务（Moonshot API、Langfuse）
   - Executor → Flask 业务 API（HTTP 请求）

4. **数据流**
   - 用户查询 → Flask → LLMRouter → Moonshot API → 预测 API
   - 预测 API → Executor → Flask 业务 API → 业务数据
   - 业务数据 → Evaluator/DeepEval → 评估结果 → Flask → 用户

---

## 📝 环境变量要求

Flask 和 AI 组件需要以下环境变量：

```bash
# LLM API 密钥
OPENAI_API_KEY=your_moonshot_api_key      # LLMRouter 使用
MOONSHOT_API_KEY=your_moonshot_api_key    # Evaluator 使用

# 数据库（可选）
SQLALCHEMY_DATABASE_URI=mysql://...

# Langfuse（可选，用于日志追踪）
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
LANGFUSE_HOST=...
```

---

## 🚀 运行流程

1. **启动 Flask 服务器**
   ```bash
   python poc/hr/apis/flask_server.py
   ```
   服务器启动在 `http://127.0.0.1:8000`

2. **调用评估 API**
   ```bash
   curl -X POST http://127.0.0.1:8000/eval/comprehensive \
     -H "Content-Type: application/json" \
     -d '{"type": "single", "query": "我今年年假还剩几天？"}'
   ```

3. **Flask 内部流程**
   - 接收请求
   - 初始化 AI 组件
   - 调用 LLM 进行路由预测
   - 执行 API 调用（调用自己的业务端点）
   - 评估结果
   - 返回评估报告

---

## 📚 相关文件

- `poc/hr/apis/flask_server.py` - Flask 服务器主文件
- `agent_platform/router/llm_router.py` - LLM 路由规划器
- `agent_platform/core/executor.py` - API 执行器
- `agent_platform/core/evaluator.py` - 评估器
- `agent_platform/core/deepeval_metrics.py` - DeepEval 指标
- `agent_platform/injection/api_registry.json` - API 注册表

