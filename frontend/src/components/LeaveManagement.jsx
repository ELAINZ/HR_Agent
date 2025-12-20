import { useState, useEffect } from 'react';
import { leaveAPI } from '../api/api';

function LeaveManagement() {
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    employee_id: 'E12345',
    leave_type: 'annual',
    start_date: '',
    end_date: '',
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    try {
      const response = await leaveAPI.getBalance('E12345');
      setBalance(response.data);
    } catch (err) {
      console.error('加载余额失败:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await leaveAPI.apply(formData);
      setResult(response.data);
      await loadBalance(); // 重新加载余额
    } catch (err) {
      setError(err.response?.data?.message || '申请失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">请假余额</h2>
        {balance ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">年假余额</div>
              <div className="text-2xl font-bold text-blue-600">
                {balance.annual_leave_remaining || balance.annual_leave_total - balance.annual_leave_used || 0} 天
              </div>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">病假余额</div>
              <div className="text-2xl font-bold text-green-600">
                {balance.sick_leave_remaining || balance.sick_leave_total - balance.sick_leave_used || 0} 天
              </div>
            </div>
          </div>
        ) : (
          <div className="text-gray-500">加载中...</div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">申请请假</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                请假类型
              </label>
              <select
                value={formData.leave_type}
                onChange={(e) => setFormData({ ...formData, leave_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="annual">年假</option>
                <option value="sick">病假</option>
                <option value="personal">事假</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                开始日期
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
                结束日期
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
              {result.application_id && (
                <div className="text-sm mt-1">申请ID: {result.application_id}</div>
              )}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full md:w-auto px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '提交中...' : '提交申请'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default LeaveManagement;

