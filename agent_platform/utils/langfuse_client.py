import uuid
from agent_platform.utils.config import Config
from langfuse import Langfuse, get_client, observe

class LangfuseClient:

    def __init__(self):
        if Config.USE_LANGFUSE:
            try:
                # 建立客户端连接
                self.client = Langfuse(
                    public_key=Config.LANGFUSE_PUBLIC_KEY,
                    secret_key=Config.LANGFUSE_SECRET_KEY,
                    host=Config.LANGFUSE_HOST
                )
                print(f"[Langfuse] Connected to {Config.LANGFUSE_HOST}")
            except Exception as e:
                print(f"[Langfuse] Init failed: {e}")
                self.client = None
        else:
            print("[Langfuse] Not configured, running local-only mode")
            self.client = None

    def trace_start(self, name: str, input_data: dict):
        """
        创建新的 trace_id
        """
        if not self.client:
            return None

        # 使用 deterministic trace_id，可复用相同 seed 确保一致性
        seed = f"{name}-{uuid.uuid4()}"
        trace_id = self.client.create_trace_id(seed=seed)
        print(f"[Langfuse] Trace started: {trace_id}")
        return trace_id

    def log(self, trace_id: str, name: str, metadata: dict):
        """
        在指定 trace_id 上记录事件
        """
        if not self.client or not trace_id:
            return
        try:
            self.client.create_event(
                trace_id=trace_id,
                name=name,
                metadata=metadata
            )
        except Exception as e:
            print(f"[Langfuse] Failed to log event: {e}")

    def score(self, trace_id: str, name: str, value: float):
        """
        在指定 trace_id 上记录评分
        """
        if not self.client or not trace_id:
            return
        try:
            self.client.create_score(
                trace_id=trace_id,
                name=name,
                value=value
            )
        except Exception as e:
            print(f"[Langfuse] Failed to record score: {e}")

    def end(self, trace_id: str):
        print(f"[Langfuse] Trace {trace_id} ended (auto-managed).")

    # 提供装饰器接口
    def observe_function(self, func=None):
        """
        用法：
        @langfuse_client.observe_function
        def my_func(...):
            ...
        """
        return observe()(func)


# === 示例用法 ===
if __name__ == "__main__":
    client = LangfuseClient()

    # 创建 trace_id
    trace_id = client.trace_start("test_trace_v38", {"query": "hello world"})

    # 打日志与评分
    client.log(trace_id, "api_call", {"endpoint": "/hr/leave/balance"})
    client.score(trace_id, "tool_accuracy", 0.95)
    client.end(trace_id)

    # 装饰器模式演示
    @client.observe_function
    def handle_request(user, query, langfuse_trace_id=None):
        print(f"Processing request for {user}: {query}")
        return "ok"

    handle_request("user_123", "query: policy info", langfuse_trace_id=trace_id)
