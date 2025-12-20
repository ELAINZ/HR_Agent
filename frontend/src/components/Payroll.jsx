import { useState } from 'react';
import { payrollAPI } from '../api/api';

function Payroll() {
  const [loading, setLoading] = useState(false);
  const [payrollInfo, setPayrollInfo] = useState(null);
  const [taxInfo, setTaxInfo] = useState(null);
  const [month, setMonth] = useState(new Date().toISOString().slice(0, 7));
  const [error, setError] = useState(null);

  const handleQueryPayroll = async () => {
    setLoading(true);
    setError(null);
    setPayrollInfo(null);
    setTaxInfo(null);

    try {
      const [payrollResponse, taxResponse] = await Promise.all([
        payrollAPI.getInfo('E12345', month),
        payrollAPI.getTax('E12345', month),
      ]);
      setPayrollInfo(payrollResponse.data);
      setTaxInfo(taxResponse.data);
    } catch (err) {
      setError(err.response?.data?.message || '查询失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">薪酬查询</h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <input
              type="month"
              value={month}
              onChange={(e) => setMonth(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleQueryPayroll}
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '查询中...' : '查询'}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {payrollInfo && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-6 space-y-4">
              <div className="text-lg font-semibold">薪酬信息 - {payrollInfo.month}</div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded-lg">
                  <div className="text-sm text-gray-600">基本工资</div>
                  <div className="text-2xl font-bold text-blue-600">
                    ¥{payrollInfo.salary?.toLocaleString() || '0'}
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg">
                  <div className="text-sm text-gray-600">发放状态</div>
                  <div className="text-lg font-semibold text-green-600">
                    {payrollInfo.status || '已发放'}
                  </div>
                </div>
              </div>

              {taxInfo && (
                <div className="border-t pt-4">
                  <div className="text-sm font-semibold mb-2">税费明细</div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600">个人所得税</div>
                      <div className="text-lg font-semibold">¥{taxInfo.tax?.toLocaleString() || '0'}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">社保公积金</div>
                      <div className="text-lg font-semibold">¥{taxInfo.social_security?.toLocaleString() || '0'}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Payroll;

