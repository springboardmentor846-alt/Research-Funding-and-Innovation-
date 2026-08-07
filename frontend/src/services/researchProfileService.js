import apiClient from './apiClient'

export const researchProfileService = {
  // Get my research profile
  getMyProfile: async () => {
    const response = await apiClient.get('/research-profile/me')
    return response.data
  },

  // Update my research profile
  updateMyProfile: async (profileData) => {
    const response = await apiClient.put('/research-profile/me', profileData)
    return response.data
  },

  // Upload profile avatar
  uploadAvatar: async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/research-profile/me/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  // Publications
  addPublication: async (data) => {
    const response = await apiClient.post('/research-profile/me/publications', data)
    return response.data
  },
  updatePublication: async (pubId, data) => {
    const response = await apiClient.put(`/research-profile/me/publications/${pubId}`, data)
    return response.data
  },
  deletePublication: async (pubId) => {
    await apiClient.delete(`/research-profile/me/publications/${pubId}`)
  },

  // Patents
  addPatent: async (data) => {
    const response = await apiClient.post('/research-profile/me/patents', data)
    return response.data
  },
  updatePatent: async (patId, data) => {
    const response = await apiClient.put(`/research-profile/me/patents/${patId}`, data)
    return response.data
  },
  deletePatent: async (patId) => {
    await apiClient.delete(`/research-profile/me/patents/${patId}`)
  },

  // Research Projects / History
  addProject: async (data) => {
    const response = await apiClient.post('/research-profile/me/projects', data)
    return response.data
  },
  updateProject: async (projId, data) => {
    const response = await apiClient.put(`/research-profile/me/projects/${projId}`, data)
    return response.data
  },
  deleteProject: async (projId) => {
    await apiClient.delete(`/research-profile/me/projects/${projId}`)
  },

  // Search & Discovery
  searchResearchers: async (params) => {
    const response = await apiClient.get('/research-profile/search', { params })
    return response.data
  },

  // Public Profile View
  getPublicProfile: async (id) => {
    const response = await apiClient.get(`/research-profile/${id}`)
    return response.data
  },
}
