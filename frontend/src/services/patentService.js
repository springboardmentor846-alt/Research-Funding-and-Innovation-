import apiClient from './apiClient'

export const patentService = {
  // Search & Filter Patents
  searchPatents: async (params = {}) => {
    const response = await apiClient.get('/patents/search', { params })
    return response.data
  },

  // Get Single Patent Details
  getPatentDetails: async (patentId) => {
    const response = await apiClient.get(`/patents/${patentId}`)
    return response.data
  },

  // AI Patent Recommendations
  getRecommendations: async (limit = 6) => {
    const response = await apiClient.get('/patents/recommendations', { params: { limit } })
    return response.data
  },

  // Patent Technology Trends
  getTrends: async (limit = 6) => {
    const response = await apiClient.get('/patents/trending', { params: { limit } })
    return response.data
  },

  // Aggregate Analytics & Breakdown
  getAnalytics: async () => {
    const response = await apiClient.get('/patents/analytics')
    return response.data
  },

  // Patent Dashboard Summary
  getDashboardSummary: async () => {
    const response = await apiClient.get('/patents/dashboard-summary')
    return response.data
  },
}
