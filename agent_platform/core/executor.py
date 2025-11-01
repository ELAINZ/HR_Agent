import requests, time
from agent_platform.utils.langfuse_client import LangfuseClient

class Executor:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.langfuse = LangfuseClient()

    def execute(self, case_id, query, route_plan):
        trace = self.langfuse.trace_start(name=f"case_{case_id}", input_data=query)
        start = time.time()
        url = f"{self.base_url}{route_plan}"
        resp = requests.get(url).json()
        latency = (time.time() - start) * 1000
        self.langfuse.log(trace, "api_call", {"url": url, "response": resp})
        self.langfuse.end(trace)
        return resp, latency
