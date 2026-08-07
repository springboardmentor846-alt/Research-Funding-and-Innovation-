import apiClient from './apiClient'

export const technologyService = {
  // Search & Filter Technology Trends
  searchTrends: async (params = {}) => {
    const response = await apiClient.get('/technology/trends', { params })
    return response.data
  },

  // Get Single Technology Trend Details
  getTrendDetails: async (trendId) => {
    const response = await apiClient.get(`/technology/trends/${trendId}`)
    return response.data
  },

  // Top Emerging Technologies
  getEmerging: async (limit = 6) => {
    const response = await apiClient.get('/technology/emerging', { params: { limit } })
    return response.data
  },

  // Calculate & Get User Innovation Score
  getInnovationScore: async () => {
    const response = await apiClient.get('/technology/innovation-score')
    return response.data
  },

  // Strategic Opportunity Analysis
  getOpportunities: async (limit = 6) => {
    const response = await apiClient.get('/technology/opportunities', { params: { limit } })
    return response.data
  },

  // Technology Dashboard Summary
  getDashboardSummary: async () => {
    const response = await apiClient.get('/technology/dashboard-summary')
    return response.data
  },
}
