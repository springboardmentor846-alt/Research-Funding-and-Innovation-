import apiClient from './apiClient'

export const commercializationService = {
  // Search & Filter Commercialization Opportunities
  searchOpportunities: async (params = {}) => {
    const response = await apiClient.get('/commercialization/opportunities', { params })
    return response.data
  },

  // Get Single Opportunity Details
  getOpportunityDetails: async (oppId) => {
    const response = await apiClient.get(`/commercialization/opportunities/${oppId}`)
    return response.data
  },

  // Industry Partners Directory
  getIndustryPartners: async (params = {}) => {
    const response = await apiClient.get('/commercialization/partners', { params })
    return response.data
  },

  // Startup Programs & Accelerators
  getStartupPrograms: async (params = {}) => {
    const response = await apiClient.get('/commercialization/startup-programs', { params })
    return response.data
  },

  // AI Commercialization Recommendations
  getRecommendations: async (limit = 6) => {
    const response = await apiClient.get('/commercialization/recommendations', { params: { limit } })
    return response.data
  },

  // Commercialization Dashboard Summary
  getDashboardSummary: async () => {
    const response = await apiClient.get('/commercialization/dashboard-summary')
    return response.data
  },

  // User Bookmarks & Collaborations
  getMyCollaborations: async () => {
    const response = await apiClient.get('/commercialization/my-collaborations')
    return response.data
  },

  // Toggle Bookmark
  toggleBookmark: async (oppId) => {
    const response = await apiClient.post(`/commercialization/bookmarks/${oppId}`)
    return response.data
  },

  // Submit Interest / Contact Request
  submitCollaborationRequest: async (oppId, data) => {
    const response = await apiClient.post(`/commercialization/collaborate/${oppId}`, data)
    return response.data
  },
}
