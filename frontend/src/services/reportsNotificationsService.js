import apiClient from './apiClient'

export const reportsNotificationsService = {
  // Notifications
  getNotifications: async () => {
    const response = await apiClient.get('/notifications')
    return response.data
  },

  markAsRead: async (notifId) => {
    const response = await apiClient.post(`/notifications/${notifId}/read`)
    return response.data
  },

  markAllAsRead: async () => {
    const response = await apiClient.post('/notifications/read-all')
    return response.data
  },

  // Reports
  getUserReports: async () => {
    const response = await apiClient.get('/reports')
    return response.data
  },

  generateReport: async (data) => {
    const response = await apiClient.post('/reports/generate', data)
    return response.data
  },

  exportCSVUrl: (reportType) => {
    return `${apiClient.defaults.baseURL}/reports/export/csv/${reportType}`
  },

  // Admin Dashboard & System Analytics
  getAdminStats: async () => {
    const response = await apiClient.get('/admin/stats')
    return response.data
  },

  getSystemAnalytics: async () => {
    const response = await apiClient.get('/admin/analytics')
    return response.data
  },

  getAdminUsers: async () => {
    const response = await apiClient.get('/admin/users')
    return response.data
  },

  updateUserStatus: async (userId, data) => {
    const response = await apiClient.put(`/admin/users/${userId}/status`, data)
    return response.data
  },
}
