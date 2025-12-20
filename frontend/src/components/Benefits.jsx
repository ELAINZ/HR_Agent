import { useState, useEffect } from 'react';
import { benefitsAPI } from '../api/api';

function Benefits() {
  const [benefits, setBenefits] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [selectedBenefit, setSelectedBenefit] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    loadBenefits();
  }, []);

  const loadBenefits = async () => {
    try {
      const response = await benefitsAPI.getList('E12345');
      setBenefits(response.data);
    } catch (err) {
      console.error('加载福利列表失败:', err);
    }
  };

  const handleApply = async () => {
    if (!selectedBenefit) {
      setError('请选择要申请的福利');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await benefitsAPI.apply({
        employee_id: 'E12345',
        benefit_type: selectedBenefit,
      });
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
        <h2 className="text-xl font-semibold mb-4">可用福利</h2>
        {benefits && benefits.benefits ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {benefits.benefits.map((benefit, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-purple-50 to-pink-50 p-4 rounded-lg border border-purple-200"
              >
                <div className="text-lg font-semibold text-purple-800">{benefit}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500">加载中...</div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">申请福利</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              选择福利
            </label>
            <select
              value={selectedBenefit}
              onChange={(e) => setSelectedBenefit(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">请选择...</option>
              {benefits?.benefits?.map((benefit, index) => (
                <option key={index} value={benefit}>
                  {benefit}
                </option>
              ))}
            </select>
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
            onClick={handleApply}
            disabled={loading || !selectedBenefit}
            className="px-6 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '提交中...' : '提交申请'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Benefits;

