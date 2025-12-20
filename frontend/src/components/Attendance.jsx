import { useState } from 'react';
import { attendanceAPI } from '../api/api';

function Attendance() {
  const [loading, setLoading] = useState(false);
  const [checkinResult, setCheckinResult] = useState(null);
  const [status, setStatus] = useState(null);
  const [queryDate, setQueryDate] = useState(new Date().toISOString().split('T')[0]);
  const [error, setError] = useState(null);

  const handleCheckin = async () => {
    setLoading(true);
    setError(null);
    setCheckinResult(null);

    try {
      const response = await attendanceAPI.checkin('E12345');
      setCheckinResult(response.data);
    } catch (err) {
      setError(err.response?.data?.message || '签到失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleQueryStatus = async () => {
    setLoading(true);
    setError(null);
    setStatus(null);

    try {
      const response = await attendanceAPI.getStatus('E12345', queryDate);
      setStatus(response.data);
    } catch (err) {
      setError(err.response?.data?.message || '查询失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">签到打卡</h2>
        <div className="space-y-4">
          <button
            onClick={handleCheckin}
            disabled={loading}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-lg font-medium"
          >
            {loading ? '签到中...' : '📝 立即签到'}
          </button>

          {checkinResult && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              <div className="font-semibold">签到成功！</div>
              <div className="text-sm mt-1">时间: {checkinResult.timestamp}</div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">考勤查询</h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <input
              type="date"
              value={queryDate}
              onChange={(e) => setQueryDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleQueryStatus}
              disabled={loading}
              className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              查询
            </button>
          </div>

          {status && (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-gray-600">日期</div>
                  <div className="font-semibold">{status.date}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600">状态</div>
                  <div className="font-semibold">{status.status}</div>
                </div>
                {status.checkin_time && (
                  <div>
                    <div className="text-sm text-gray-600">签到时间</div>
                    <div className="font-semibold">{status.checkin_time}</div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Attendance;

