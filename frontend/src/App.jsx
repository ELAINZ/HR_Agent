import { useState, useEffect } from 'react';
import LeaveManagement from './components/LeaveManagement';
import Attendance from './components/Attendance';
import Payroll from './components/Payroll';
import Policy from './components/Policy';
import Benefits from './components/Benefits';
import Travel from './components/Travel';
import Expense from './components/Expense';
import Evaluation from './components/Evaluation';
import { healthCheck } from './api/api';

function App() {
  const [activeTab, setActiveTab] = useState('leave');
  const [apiStatus, setApiStatus] = useState('checking');

  const tabs = [
    { id: 'leave', name: '请假管理', icon: '📅' },
    { id: 'attendance', name: '考勤', icon: '⏰' },
    { id: 'payroll', name: '薪酬', icon: '💰' },
    { id: 'policy', name: '政策查询', icon: '📋' },
    { id: 'benefits', name: '福利', icon: '🎁' },
    { id: 'travel', name: '差旅', icon: '✈️' },
    { id: 'expense', name: '报销', icon: '💳' },
    { id: 'evaluation', name: '评估测试', icon: '🧪' },
  ];

  // 检查API状态
  useEffect(() => {
    healthCheck()
      .then(() => setApiStatus('connected'))
      .catch(() => setApiStatus('disconnected'));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 头部导航 */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-gray-900">
                HR Agent 人力资源管理系统
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm ${
                apiStatus === 'connected' 
                  ? 'bg-green-100 text-green-800' 
                  : apiStatus === 'disconnected'
                  ? 'bg-red-100 text-red-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}>
                {apiStatus === 'connected' && '✓ API已连接'}
                {apiStatus === 'disconnected' && '✗ API未连接'}
                {apiStatus === 'checking' && '检查中...'}
              </div>
              <div className="text-sm text-gray-600">
                员工ID: E12345
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* 标签导航 */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-3 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* 主内容区 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'leave' && <LeaveManagement />}
        {activeTab === 'attendance' && <Attendance />}
        {activeTab === 'payroll' && <Payroll />}
        {activeTab === 'policy' && <Policy />}
        {activeTab === 'benefits' && <Benefits />}
        {activeTab === 'travel' && <Travel />}
        {activeTab === 'expense' && <Expense />}
        {activeTab === 'evaluation' && <Evaluation />}
      </main>
    </div>
  );
}

export default App;

