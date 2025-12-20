import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请假相关API
export const leaveAPI = {
  getBalance: (employeeId = 'E12345') => 
    api.get('/hr/leave/balance', { params: { employee_id: employeeId } }),
  
  apply: (data) => 
    api.post('/hr/leave/apply', data),
};

// 考勤相关API
export const attendanceAPI = {
  checkin: (employeeId = 'E12345') => 
    api.post('/hr/attendance/checkin', { employee_id: employeeId }),
  
  getStatus: (employeeId = 'E12345', date) => 
    api.get('/hr/attendance/status', { 
      params: { employee_id: employeeId, date } 
    }),
};

// 薪酬相关API
export const payrollAPI = {
  getInfo: (employeeId = 'E12345', month) => 
    api.get('/hr/payroll/info', { 
      params: { employee_id: employeeId, month } 
    }),
  
  getTax: (employeeId = 'E12345', month) => 
    api.get('/hr/payroll/tax', { 
      params: { employee_id: employeeId, month } 
    }),
};

// 政策相关API
export const policyAPI = {
  getPolicy: (topic) => 
    api.get('/hr/policy', { params: { topic } }),
};

// 福利相关API
export const benefitsAPI = {
  getList: (employeeId = 'E12345') => 
    api.get('/hr/benefits/list', { params: { employee_id: employeeId } }),
  
  apply: (data) => 
    api.post('/hr/benefits/apply', data),
};

// 差旅相关API
export const travelAPI = {
  getPolicy: (topic) => 
    api.get('/hr/travel/policy', { params: { topic } }),
  
  apply: (data) => 
    api.post('/hr/travel/apply', data),
};

// 报销相关API
export const expenseAPI = {
  submit: (data) => 
    api.post('/hr/expense/submit', data),
};

// 评估和LLM测试相关API
export const evalAPI = {
  // LLM路由测试
  testRoute: (query) => 
    api.post('/eval/llm/route', { query }),
  
  // 运行评估（基础）
  runEvaluation: (data) => 
    api.post('/eval/run', data),
  
  // 运行综合评估（路由 + 返回数据 + 幻觉检测）
  runComprehensiveEvaluation: (data) => 
    api.post('/eval/comprehensive', data),
  
  // 获取测试用例
  getTestCases: () => 
    api.get('/eval/testcases'),
};

// 健康检查
export const healthCheck = () => api.get('/health');

export default api;

