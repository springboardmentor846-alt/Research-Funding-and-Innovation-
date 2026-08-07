import apiClient from './apiClient'

export const fundingService = {
  // Search & Filter
  searchOpportunities: async (params = {}) => {
    const response = await apiClient.get('/funding/search', { params })
    return response.data
  },

  // AI Recommendations
  getRecommendations: async (limit = 6) => {
    const response = await apiClient.get('/funding/recommendations', { params: { limit } })
    return response.data
  },

  // Dashboard summary metrics & lists
  getDashboardSummary: async () => {
    const response = await apiClient.get('/funding/dashboard-summary')
    return response.data
  },

  // Detail View
  getOpportunityDetails: async (id) => {
    const response = await apiClient.get(`/funding/${id}`)
    return response.data
  },

  // Bookmarks
  toggleBookmark: async (id) => {
    const response = await apiClient.post(`/funding/${id}/bookmark`)
    return response.data
  },

  getMyBookmarks: async () => {
    const response = await apiClient.get('/funding/bookmarks/me')
    return response.data
  },

  // Alerts
  getMyAlerts: async () => {
    const response = await apiClient.get('/funding/alerts/me')
    return response.data
  },

  createAlert: async (alertData) => {
    const response = await apiClient.post('/funding/alerts', alertData)
    return response.data
  },

  deleteAlert: async (alertId) => {
    await apiClient.delete(`/funding/alerts/${alertId}`)
  },
}
