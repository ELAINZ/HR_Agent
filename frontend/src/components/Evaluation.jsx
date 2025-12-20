import { useState, useEffect } from 'react';
import { evalAPI } from '../api/api';

function Evaluation() {
  const [loading, setLoading] = useState(false);
  const [testQuery, setTestQuery] = useState('我今年年假还剩几天？');
  const [routeResult, setRouteResult] = useState(null);
  const [evaluationResults, setEvaluationResults] = useState(null);
  const [comprehensiveResults, setComprehensiveResults] = useState(null);
  const [testCases, setTestCases] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadTestCases();
  }, []);

  const loadTestCases = async () => {
    try {
      const response = await evalAPI.getTestCases();
      setTestCases(response.data.testcases || []);
    } catch (err) {
      console.error('加载测试用例失败:', err);
    }
  };

  const handleRouteTest = async () => {
    if (!testQuery.trim()) {
      setError('请输入测试查询');
      return;
    }

    setLoading(true);
    setError(null);
    setRouteResult(null);

    try {
      const response = await evalAPI.testRoute(testQuery);
      setRouteResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || '路由测试失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRunEvaluation = async (type = 'full') => {
    setLoading(true);
    setError(null);
    setEvaluationResults(null);
    setComprehensiveResults(null);

    try {
      const data = type === 'single' 
        ? { type: 'single', query: testQuery }
        : { type: 'full' };
      
      const response = await evalAPI.runEvaluation(data);
      setEvaluationResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || '评估运行失败');
    } finally {
      setLoading(false);
    }
  };

  const handleRunComprehensiveEvaluation = async (type = 'full') => {
    setLoading(true);
    setError(null);
    setEvaluationResults(null);
    setComprehensiveResults(null);

    try {
      const data = type === 'single' 
        ? { type: 'single', query: testQuery }
        : { type: 'full' };
      
      const response = await evalAPI.runComprehensiveEvaluation(data);
      setComprehensiveResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || '综合评估运行失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* LLM路由测试 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">🤖 LLM 路由测试</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              输入测试查询
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={testQuery}
                onChange={(e) => setTestQuery(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例如：我今年年假还剩几天？"
              />
              <button
                onClick={handleRouteTest}
                disabled={loading}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? '测试中...' : '测试路由'}
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {routeResult && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="space-y-2">
                <div>
                  <span className="text-sm text-gray-700 font-medium">查询：</span>
                  <span className="font-medium text-gray-900 ml-1">{routeResult.query}</span>
                </div>
                <div>
                  <span className="text-sm text-gray-700 font-medium">预测API：</span>
                  <span className="font-mono text-blue-700 font-semibold ml-1">{routeResult.predicted_api}</span>
                </div>
                <div className="text-sm text-green-700 font-semibold">✓ 路由成功</div>
              </div>
            </div>
          )}

          {/* 快速测试用例 */}
          <div>
            <div className="text-sm text-gray-700 font-medium mb-2">快速测试：</div>
            <div className="flex flex-wrap gap-2">
              {testCases.slice(0, 5).map((testCase, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setTestQuery(testCase.query);
                    handleRouteTest();
                  }}
                  className="px-3 py-1 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 text-sm"
                >
                  {testCase.query}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* 基础评估测试 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4 text-gray-900">📊 基础评估测试</h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <button
              onClick={() => handleRunEvaluation('single')}
              disabled={loading}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '运行中...' : '单条评估'}
            </button>
            <button
              onClick={() => handleRunEvaluation('full')}
              disabled={loading}
              className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '运行中...' : '完整评估（前10条）'}
            </button>
          </div>

          {evaluationResults && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="text-sm text-gray-700 font-medium">总数</div>
                  <div className="text-2xl font-bold text-gray-900">{evaluationResults.total}</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <div className="text-sm text-gray-700 font-medium">通过</div>
                  <div className="text-2xl font-bold text-green-700">{evaluationResults.passed}</div>
                </div>
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <div className="text-sm text-gray-700 font-medium">失败</div>
                  <div className="text-2xl font-bold text-red-700">{evaluationResults.failed}</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="text-sm text-gray-700 font-medium">准确率</div>
                  <div className="text-2xl font-bold text-blue-700">
                    {evaluationResults.accuracy || 0}%
                  </div>
                </div>
              </div>

              {/* 详细结果 */}
              <div className="mt-4">
                <div className="text-sm font-semibold mb-2 text-gray-900">详细结果：</div>
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {evaluationResults.results?.map((result, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border ${
                        result.pass
                          ? 'bg-green-50 border-green-200'
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{result.query}</div>
                          <div className="text-sm text-gray-700 mt-1">
                            预期: <span className="font-mono text-gray-900">{result.expected}</span>
                          </div>
                          <div className="text-sm text-gray-700">
                            预测: <span className="font-mono text-gray-900">{result.predicted}</span>
                          </div>
                          {result.error && (
                            <div className="text-sm text-red-700 font-medium mt-1">错误: {result.error}</div>
                          )}
                        </div>
                        <div className={`px-2 py-1 rounded text-sm ${
                          result.pass
                            ? 'bg-green-200 text-green-800'
                            : 'bg-red-200 text-red-800'
                        }`}>
                          {result.pass ? '✓ 通过' : '✗ 失败'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 综合评估测试（包含幻觉检测和回答质量） */}
      <div className="bg-white rounded-lg shadow-lg border-2 border-gray-200 p-6">
        <h2 className="text-2xl font-bold mb-4 text-gray-900">🔬 综合评估测试（路由 + 回答质量 + 幻觉检测）</h2>
        <div className="space-y-4">
          <div className="bg-yellow-100 border-2 border-yellow-400 rounded-lg p-3 mb-4">
            <div className="text-sm text-yellow-900 font-semibold">
              <strong className="text-yellow-900">包含评测：</strong>路由准确率、返回数据结构验证、幻觉检测
            </div>
          </div>
          
          <div className="flex gap-4">
            <button
              onClick={() => handleRunComprehensiveEvaluation('single')}
              disabled={loading}
              className="px-6 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '运行中...' : '单条综合评估'}
            </button>
            <button
              onClick={() => handleRunComprehensiveEvaluation('full')}
              disabled={loading}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '运行中...' : '完整综合评估（前10条）'}
            </button>
          </div>

          {comprehensiveResults && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="text-sm text-gray-700 font-medium">总数</div>
                  <div className="text-2xl font-bold text-gray-900">{comprehensiveResults.total}</div>
                </div>
                <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                  <div className="text-sm text-gray-700 font-medium">路由通过</div>
                  <div className="text-2xl font-bold text-green-700">{comprehensiveResults.passed}</div>
                </div>
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <div className="text-sm text-gray-700 font-medium">回答质量</div>
                  <div className="text-2xl font-bold text-blue-700">
                    {comprehensiveResults.json_quality !== undefined ? comprehensiveResults.json_quality : 'N/A'}%
                  </div>
                  <div className="text-xs text-gray-700 font-medium mt-1">
                    ({comprehensiveResults.json_tested || 0} 条已测试)
                  </div>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                  <div className="text-sm text-gray-700 font-medium">幻觉检测</div>
                  <div className="text-2xl font-bold text-purple-700">
                    {comprehensiveResults.hallucination_rate !== undefined ? comprehensiveResults.hallucination_rate : 'N/A'}%
                  </div>
                  <div className="text-xs text-gray-700 font-medium mt-1">
                    ({comprehensiveResults.hallucination_tested || 0} 条已测试)
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="text-sm font-semibold mb-2 text-gray-700">路由准确率</div>
                  <div className="text-3xl font-bold text-green-700">
                    {comprehensiveResults.accuracy || 0}%
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-gray-200">
                  <div className="text-sm font-semibold mb-2 text-gray-700">失败数</div>
                  <div className="text-3xl font-bold text-red-700">
                    {comprehensiveResults.failed || 0}
                  </div>
                </div>
              </div>

              {/* 详细结果 */}
              <div className="mt-4">
                <div className="text-sm font-semibold mb-2 text-gray-900">详细结果：</div>
                <div className="max-h-96 overflow-y-auto space-y-2">
                  {comprehensiveResults.results?.map((result, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border ${
                        result.pass
                          ? 'bg-green-50 border-green-200'
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{result.query}</div>
                          <div className="text-sm text-gray-700 mt-1">
                            预期API: <span className="font-mono text-gray-900 font-semibold">{result.expected}</span>
                          </div>
                          <div className="text-sm text-gray-700">
                            预测API: <span className="font-mono text-gray-900 font-semibold">{result.predicted}</span>
                          </div>
                          
                          {/* 回答质量评分 */}
                          {result.json_score !== undefined && result.json_score >= 0 && (
                            <div className="mt-2 flex items-center gap-2">
                              <span className="text-xs text-gray-800 font-semibold">回答质量:</span>
                              <div className="flex-1 bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${
                                    result.json_score >= 0.8 ? 'bg-blue-500' : 
                                    result.json_score >= 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${result.json_score * 100}%` }}
                                ></div>
                              </div>
                              <span className="text-xs font-mono text-gray-900 font-semibold">
                                {Math.round(result.json_score * 100)}%
                              </span>
                            </div>
                          )}
                          {result.json_score === -1 && (
                            <div className="mt-2 text-xs text-gray-700 font-medium">回答质量: 未测试（无规范配置）</div>
                          )}
                          
                          {/* 幻觉检测评分 */}
                          {result.hallucination_score !== undefined && result.hallucination_score >= 0 && result.hallucination_score < 1.0 && (
                            <div className="mt-2 flex items-center gap-2">
                              <span className="text-xs text-red-700 font-bold">⚠️ 检测到可能的幻觉</span>
                              <span className="text-xs text-gray-800 font-medium">
                                (评分: {Math.round(result.hallucination_score * 100)}%)
                              </span>
                            </div>
                          )}
                          {result.hallucination_score === -1 && (
                            <div className="mt-2 text-xs text-gray-700 font-medium">幻觉检测: 未测试（无规范配置）</div>
                          )}
                          
                          {result.error && (
                            <div className="text-sm text-red-700 font-medium mt-1">错误: {result.error}</div>
                          )}
                        </div>
                        <div className={`px-2 py-1 rounded text-sm ${
                          result.pass
                            ? 'bg-green-200 text-green-800'
                            : 'bg-red-200 text-red-800'
                        }`}>
                          {result.pass ? '✓ 通过' : '✗ 失败'}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Evaluation;

