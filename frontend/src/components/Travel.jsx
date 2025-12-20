import { useState } from 'react';
import { travelAPI } from '../api/api';

function Travel() {
  const [loading, setLoading] = useState(false);
  const [policy, setPolicy] = useState(null);
  const [formData, setFormData] = useState({
    employee_id: 'E12345',
    destination: '',
    start_date: '',
    end_date: '',
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleQueryPolicy = async () => {
    setLoading(true);
    setError(null);
    setPolicy(null);

    try {
      const response = await travelAPI.getPolicy('差旅标准');
      setPolicy(response.data);
    } catch (err) {
      setError(err.response?.data?.message || '查询失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await travelAPI.apply(formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.message || '申请失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">差旅政策</h2>
        <div className="space-y-4">
          <button
            onClick={handleQueryPolicy}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '查询中...' : '查询差旅标准'}
          </button>

          {policy && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
              {policy.snippets && policy.snippets.length > 0 ? (
                <div className="space-y-3">
                  {policy.snippets.map((snippet, index) => (
                    <div key={index} className="bg-white p-4 rounded-lg">
                      <div className="text-gray-800">{snippet.text}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500">暂无政策信息</div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">申请差旅</h2>
        <form onSubmit={handleApply} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                目的地
              </label>
              <input
                type="text"
                value={formData.destination}
                onChange={(e) => setFormData({ ...formData, destination: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例如：上海"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                出发日期
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                返回日期
              </label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {result && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              <div className="font-semibold">申请成功！</div>
              <div className="text-sm mt-1">{result.message}</div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '提交中...' : '提交申请'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Travel;

