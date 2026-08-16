import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT Auth Interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add Response Error Interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  googleLogin: (data) => api.post('/auth/google-login', data),
  forgotPassword: (data) => api.post('/auth/forgot-password', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
};

export const userAPI = {
  getMe: () => api.get('/users/me'),
  updateMe: (data) => api.put('/users/me', data),
  getProfile: () => api.get('/users/me/research-profile'),
  updateProfile: (data) => api.put('/users/me/research-profile', data),
};

export const fundingAPI = {
  getAll: (params) => api.get('/funding', { params }),
  getRecommendations: () => api.get('/funding/recommendations'),
  getById: (id) => api.get(`/funding/${id}`),
  create: (data) => api.post('/funding', data),
};

export const intelligenceAPI = {
  getPublications: (params) => api.get('/research-intelligence/publications', { params }),
  getResearchAnalytics: () => api.get('/research-intelligence/analytics'),
  analyzePaper: (data) => api.post('/research-intelligence/analyze-paper', data),
  getPatents: (params) => api.get('/patent-intelligence/patents', { params }),
  getPatentAnalytics: () => api.get('/patent-intelligence/analytics'),
  getTechTrends: (params) => api.get('/tech-intelligence/trends', { params }),
  getTechRadar: () => api.get('/tech-intelligence/radar'),
};

export const scoringAPI = {
  getScores: () => api.get('/innovation-score'),
  calculateScore: (data) => api.post('/innovation-score/calculate', data),
};

export const commercialAPI = {
  getAll: (params) => api.get('/commercialization', { params }),
  create: (data) => api.post('/commercialization', data),
};

export const dashboardAPI = {
  getOverview: () => api.get('/dashboards/overview'),
};

export const notificationAPI = {
  getAll: () => api.get('/notifications'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
};

export const reportAPI = {
  getAll: () => api.get('/reports'),
  generate: (data) => api.post('/reports/generate', data),
};

export const adminAPI = {
  getUsers: () => api.get('/admin/users'),
  toggleStatus: (id, is_active) => api.put(`/admin/users/${id}/status`, null, { params: { is_active } }),
  getAuditLogs: () => api.get('/admin/audit-logs'),
  seedDatabase: () => api.post('/admin/seed-database'),
};

export default api;
