import apiClient from './apiClient'

export const researchIntelligenceService = {
  // Search & Filter Papers
  searchPapers: async (params = {}) => {
    const response = await apiClient.get('/research-intelligence/search', { params })
    return response.data
  },

  // AI Paper Recommendations
  getRecommendations: async (limit = 6) => {
    const response = await apiClient.get('/research-intelligence/recommendations', { params: { limit } })
    return response.data
  },

  // Trending Research Topics
  getTrending: async (limit = 6) => {
    const response = await apiClient.get('/research-intelligence/trending', { params: { limit } })
    return response.data
  },

  // Emerging Topics
  getEmerging: async (limit = 6) => {
    const response = await apiClient.get('/research-intelligence/emerging', { params: { limit } })
    return response.data
  },

  // Dashboard summary metrics & lists
  getDashboardSummary: async () => {
    const response = await apiClient.get('/research-intelligence/dashboard-summary')
    return response.data
  },

  // Paper Detail View
  getPaperDetails: async (id) => {
    const response = await apiClient.get(`/research-intelligence/papers/${id}`)
    return response.data
  },
}
