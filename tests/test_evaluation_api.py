#!/usr/bin/env python3
"""
评估 API 测试套件

专门测试后端评估相关的 API 端点：
- /eval/llm/route - LLM 路由测试
- /eval/testcases - 获取测试用例
- /eval/run - 基础评估
- /eval/comprehensive - 综合评估

使用方法：
    python tests/test_evaluation_api.py
    或
    pytest tests/test_evaluation_api.py -v
"""

import requests
import json
import sys
import os

# 添加项目根目录到路径
PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

BASE_URL = "http://127.0.0.1:8000"


def check_server_available():
    """检查服务器是否可用"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False


# 模块级别的服务器检查（适用于pytest）
# 如果使用pytest运行，在模块加载时检查服务器
try:
    import pytest
    _server_available = check_server_available()
    if not _server_available:
        pytest.skip(
            f"后端服务未运行 ({BASE_URL})\n"
            f"请先启动 Flask 后端: python poc/hr/apis/flask_server.py",
            allow_module_level=True
        )
except ImportError:
    # 如果没有安装pytest，跳过模块级别的检查
    # 将在setup_class或main函数中检查
    pass


class TestEvaluationAPI:
    """评估 API 测试类"""
    
    @classmethod
    def setup_class(cls):
        """测试类初始化"""
        # 再次检查服务器（双重保险）
        if not check_server_available():
            raise ConnectionError(
                f"无法连接到后端服务 ({BASE_URL})\n"
                f"请确保 Flask 后端已启动: python poc/hr/apis/flask_server.py"
            )
        
        cls.base_url = BASE_URL
        cls.session = requests.Session()
        print(f"\n{'='*60}")
        print("开始测试评估 API")
        print(f"{'='*60}\n")
    
    def test_eval_llm_route(self):
        """测试 LLM 路由测试端点"""
        print("测试: POST /eval/llm/route")
        response = self.session.post(
            f"{self.base_url}/eval/llm/route",
            json={"query": "我今年年假还剩几天？"}
        )
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "predicted_api" in data, "响应应包含predicted_api字段"
        assert "query" in data, "响应应包含query字段"
        assert "status" in data, "响应应包含status字段"
        assert data["status"] == "success", "status应为success"
        print(f"  ✓ LLM路由测试通过")
        print(f"    查询: {data.get('query')}")
        print(f"    预测API: {data.get('predicted_api')}\n")
    
    def test_eval_llm_route_missing_query(self):
        """测试 LLM 路由 - 缺少query参数"""
        print("测试: POST /eval/llm/route (缺少query)")
        response = self.session.post(
            f"{self.base_url}/eval/llm/route",
            json={}
        )
        assert response.status_code == 400, f"状态码应为400，实际为{response.status_code}"
        data = response.json()
        assert "error" in data, "响应应包含error字段"
        print(f"  ✓ 错误处理测试通过 (错误信息: {data.get('error')})\n")
    
    def test_eval_testcases(self):
        """测试获取测试用例端点"""
        print("测试: GET /eval/testcases")
        response = self.session.get(f"{self.base_url}/eval/testcases")
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "testcases" in data, "响应应包含testcases字段"
        assert isinstance(data["testcases"], list), "testcases应为列表"
        assert "total" in data, "响应应包含total字段"
        print(f"  ✓ 获取测试用例通过")
        print(f"    测试用例数量: {len(data['testcases'])}")
        print(f"    总用例数: {data.get('total')}\n")
    
    def test_eval_run_single(self):
        """测试基础评估 - 单条测试"""
        print("测试: POST /eval/run (单条)")
        response = self.session.post(
            f"{self.base_url}/eval/run",
            json={
                "type": "single",
                "query": "我今年年假还剩几天？",
                "expected_api": "/hr/leave/balance"
            }
        )
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "results" in data, "响应应包含results字段"
        assert "total" in data, "响应应包含total字段"
        assert "passed" in data, "响应应包含passed字段"
        assert "failed" in data, "响应应包含failed字段"
        assert data["total"] == 1, "单条测试total应为1"
        
        if data["results"]:
            result = data["results"][0]
            assert "query" in result, "结果应包含query字段"
            assert "expected" in result, "结果应包含expected字段"
            assert "predicted" in result, "结果应包含predicted字段"
            assert "pass" in result, "结果应包含pass字段"
        
        print(f"  ✓ 基础评估单条测试通过")
        print(f"    通过: {data.get('passed')}/{data.get('total')}")
        if data["results"]:
            result = data["results"][0]
            print(f"    路由结果: {'✓ 通过' if result.get('pass') else '✗ 失败'}")
            print(f"    预期: {result.get('expected')}")
            print(f"    预测: {result.get('predicted')}\n")
    
    def test_eval_run_full(self):
        """测试基础评估 - 完整测试"""
        print("测试: POST /eval/run (完整)")
        response = self.session.post(
            f"{self.base_url}/eval/run",
            json={"type": "full"}
        )
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "results" in data, "响应应包含results字段"
        assert "total" in data, "响应应包含total字段"
        assert "passed" in data, "响应应包含passed字段"
        assert "failed" in data, "响应应包含failed字段"
        assert "accuracy" in data, "响应应包含accuracy字段"
        assert isinstance(data["results"], list), "results应为列表"
        
        print(f"  ✓ 基础评估完整测试通过")
        print(f"    总测试数: {data.get('total')}")
        print(f"    通过: {data.get('passed')}")
        print(f"    失败: {data.get('failed')}")
        print(f"    准确率: {data.get('accuracy')}%\n")
    
    def test_eval_comprehensive_single(self):
        """测试综合评估 - 单条测试"""
        print("测试: POST /eval/comprehensive (单条)")
        response = self.session.post(
            f"{self.base_url}/eval/comprehensive",
            json={
                "type": "single",
                "query": "我今年年假还剩几天？",
                "expected_api": "/hr/leave/balance"
            }
        )
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "results" in data, "响应应包含results字段"
        assert "total" in data, "响应应包含total字段"
        assert "json_quality" in data, "响应应包含json_quality字段"
        assert "hallucination_rate" in data, "响应应包含hallucination_rate字段"
        assert "json_tested" in data, "响应应包含json_tested字段"
        assert "hallucination_tested" in data, "响应应包含hallucination_tested字段"
        
        if data["results"]:
            result = data["results"][0]
            assert "json_score" in result, "结果应包含json_score字段"
            assert "hallucination_score" in result, "结果应包含hallucination_score字段"
            assert "response" in result, "结果应包含response字段"
        
        print(f"  ✓ 综合评估单条测试通过")
        print(f"    通过: {data.get('passed')}/{data.get('total')}")
        if data["results"]:
            result = data["results"][0]
            print(f"    路由: {'✓ 通过' if result.get('pass') else '✗ 失败'}")
            json_score = result.get('json_score', -1)
            hallucination_score = result.get('hallucination_score', -1)
            print(f"    JSON质量: {json_score if json_score >= 0 else '未测试'}")
            print(f"    幻觉检测: {hallucination_score if hallucination_score >= 0 else '未测试'}\n")
    
    def test_eval_comprehensive_full(self):
        """测试综合评估 - 完整测试"""
        print("测试: POST /eval/comprehensive (完整)")
        response = self.session.post(
            f"{self.base_url}/eval/comprehensive",
            json={"type": "full"}
        )
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "results" in data, "响应应包含results字段"
        assert "total" in data, "响应应包含total字段"
        assert "accuracy" in data, "响应应包含accuracy字段"
        assert "json_quality" in data, "响应应包含json_quality字段"
        assert "hallucination_rate" in data, "响应应包含hallucination_rate字段"
        assert "json_tested" in data, "响应应包含json_tested字段"
        assert "hallucination_tested" in data, "响应应包含hallucination_tested字段"
        
        print(f"  ✓ 综合评估完整测试通过")
        print(f"    总测试数: {data.get('total')}")
        print(f"    路由准确率: {data.get('accuracy')}%")
        print(f"    JSON质量: {data.get('json_quality')}%")
        print(f"    幻觉检测通过率: {data.get('hallucination_rate')}%")
        print(f"    JSON测试数: {data.get('json_tested')}")
        print(f"    幻觉测试数: {data.get('hallucination_tested')}\n")
    
    def test_eval_run_invalid_type(self):
        """测试基础评估 - 无效类型（应使用默认值）"""
        print("测试: POST /eval/run (无效type)")
        response = self.session.post(
            f"{self.base_url}/eval/run",
            json={"type": "invalid"}
        )
        # 应该返回200，使用默认值"full"
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "results" in data, "响应应包含results字段"
        print("  ✓ 无效类型处理测试通过（使用默认值）\n")
    
    def test_eval_comprehensive_invalid_type(self):
        """测试综合评估 - 无效类型（应使用默认值）"""
        print("测试: POST /eval/comprehensive (无效type)")
        response = self.session.post(
            f"{self.base_url}/eval/comprehensive",
            json={"type": "invalid"}
        )
        # 应该返回200，使用默认值"full"
        assert response.status_code == 200, f"状态码应为200，实际为{response.status_code}"
        data = response.json()
        assert "results" in data, "响应应包含results字段"
        print("  ✓ 无效类型处理测试通过（使用默认值）\n")


def run_tests():
    """运行所有评估API测试"""
    test_instance = TestEvaluationAPI()
    test_instance.setup_class()
    
    results = []
    
    # 评估 API 测试
    eval_tests = [
        ("LLM路由测试", test_instance.test_eval_llm_route),
        ("LLM路由-缺少query", test_instance.test_eval_llm_route_missing_query),
        ("获取测试用例", test_instance.test_eval_testcases),
        ("基础评估-单条", test_instance.test_eval_run_single),
        ("基础评估-完整", test_instance.test_eval_run_full),
        ("综合评估-单条", test_instance.test_eval_comprehensive_single),
        ("综合评估-完整", test_instance.test_eval_comprehensive_full),
        ("错误处理-无效type(基础)", test_instance.test_eval_run_invalid_type),
        ("错误处理-无效type(综合)", test_instance.test_eval_comprehensive_invalid_type),
    ]
    
    for name, test_func in eval_tests:
        try:
            test_func()
            results.append((name, True))
        except AssertionError as e:
            results.append((name, False, str(e)))
        except Exception as e:
            results.append((name, False, f"异常: {str(e)}"))
    
    # 汇总结果
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r[1])
    failed = len(results) - passed
    
    for name, success, *error in results:
        status = "✓ 通过" if success else "✗ 失败"
        if not success and error:
            print(f"{name}: {status} ({error[0]})")
        else:
            print(f"{name}: {status}")
    
    print(f"\n总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"{'='*60}\n")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    
    # 检查后端是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print(f"错误: 后端服务未正常运行 (状态码: {response.status_code})")
            print(f"请确保 Flask 后端已启动: python poc/hr/apis/flask_server.py")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到后端服务 ({BASE_URL})")
        print(f"请确保 Flask 后端已启动: python poc/hr/apis/flask_server.py")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 检查后端服务时出错: {e}")
        sys.exit(1)
    
    # 运行测试
    success = run_tests()
    sys.exit(0 if success else 1)

