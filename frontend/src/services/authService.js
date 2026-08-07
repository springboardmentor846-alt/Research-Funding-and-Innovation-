import apiClient from './apiClient'

/**
 * Authentication API service.
 */
export const authService = {
  async register(data) {
    const res = await apiClient.post('/auth/register', data)
    return res.data
  },

  async login(email, password) {
    const res = await apiClient.post('/auth/login', { email, password })
    return res.data
  },

  async refreshToken(refreshToken) {
    const res = await apiClient.post('/auth/refresh', { refresh_token: refreshToken })
    return res.data
  },

  async logout(refreshToken) {
    const res = await apiClient.post('/auth/logout', { refresh_token: refreshToken })
    return res.data
  },

  async forgotPassword(email) {
    const res = await apiClient.post('/auth/forgot-password', { email })
    return res.data
  },

  async resetPassword(token, newPassword, confirmPassword) {
    const res = await apiClient.post('/auth/reset-password', {
      token,
      new_password: newPassword,
      confirm_password: confirmPassword,
    })
    return res.data
  },

  async verifyEmail(token) {
    const res = await apiClient.post('/auth/verify-email', { token })
    return res.data
  },

  async getMe() {
    const res = await apiClient.get('/auth/me')
    return res.data
  },
}

/**
 * User / profile API service.
 */
export const userService = {
  async getProfile() {
    const res = await apiClient.get('/users/me')
    return res.data
  },

  async updateProfile(data) {
    const res = await apiClient.patch('/users/me', data)
    return res.data
  },

  async changePassword(currentPassword, newPassword, confirmNewPassword) {
    const res = await apiClient.put('/users/me/password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_new_password: confirmNewPassword,
    })
    return res.data
  },

  // Admin
  async listUsers(params = {}) {
    const res = await apiClient.get('/users/', { params })
    return res.data
  },

  async getUserById(id) {
    const res = await apiClient.get(`/users/${id}`)
    return res.data
  },

  async adminUpdateUser(id, data) {
    const res = await apiClient.patch(`/users/${id}`, data)
    return res.data
  },

  async deleteUser(id) {
    await apiClient.delete(`/users/${id}`)
  },
}
