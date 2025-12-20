import { useState } from 'react';
import { policyAPI } from '../api/api';

function Policy() {
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState('婚假');
  const [policy, setPolicy] = useState(null);
  const [error, setError] = useState(null);

  const commonTopics = ['婚假', '产假', '丧假', '年假', '病假', '事假'];

  const handleQuery = async (queryTopic = topic) => {
    setLoading(true);
    setError(null);
    setPolicy(null);

    try {
      const response = await policyAPI.getPolicy(queryTopic);
      setPolicy(response.data);
    } catch (err) {
      setError(err.response?.data?.message || '查询失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">政策查询</h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="输入政策关键词"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={() => handleQuery()}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '查询中...' : '查询'}
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {commonTopics.map((t) => (
              <button
                key={t}
                onClick={() => {
                  setTopic(t);
                  handleQuery(t);
                }}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
              >
                {t}
              </button>
            ))}
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {policy && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              <div className="text-lg font-semibold mb-4">
                查询结果：{policy.topic}
              </div>
              {policy.snippets && policy.snippets.length > 0 ? (
                <div className="space-y-3">
                  {policy.snippets.map((snippet, index) => (
                    <div key={index} className="bg-white p-4 rounded-lg">
                      <div className="text-sm text-gray-500 mb-2">
                        来源: {snippet.source || 'HR手册'}
                      </div>
                      <div className="text-gray-800">{snippet.text}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500">暂无相关政策信息</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Policy;

