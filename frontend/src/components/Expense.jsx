import { useState } from 'react';
import { expenseAPI } from '../api/api';

function Expense() {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    employee_id: 'E12345',
    amount: '',
    category: '住宿',
    voucher_id: '',
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const categories = ['住宿', '交通', '餐饮', '其他'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await expenseAPI.submit({
        ...formData,
        amount: parseFloat(formData.amount),
      });
      setResult(response.data);
      // 重置表单
      setFormData({
        employee_id: 'E12345',
        amount: '',
        category: '住宿',
        voucher_id: '',
      });
    } catch (err) {
      setError(err.response?.data?.message || '提交失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">提交报销</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                报销类别
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                报销金额（元）
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.amount}
                onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                凭证ID
              </label>
              <input
                type="text"
                value={formData.voucher_id}
                onChange={(e) => setFormData({ ...formData, voucher_id: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例如：VC001"
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
              <div className="font-semibold">提交成功！</div>
              <div className="text-sm mt-1">报销ID: {result.expense_id}</div>
              <div className="text-sm mt-1">状态: {result.status}</div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '提交中...' : '提交报销'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Expense;

