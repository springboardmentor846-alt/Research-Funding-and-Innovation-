import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authService } from '@/services/authService'
import toast from 'react-hot-toast'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]         = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // ── Bootstrap: re-hydrate session on mount ───────────────────────────────
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      authService.getMe()
        .then((data) => {
          setUser(data)
          setIsAuthenticated(true)
        })
        .catch(() => {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  // ── Login ─────────────────────────────────────────────────────────────────
  const login = useCallback(async (email, password) => {
    const data = await authService.login(email, password)
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    const profile = await authService.getMe()
    setUser(profile)
    setIsAuthenticated(true)
    return profile
  }, [])

  // ── Register ──────────────────────────────────────────────────────────────
  const register = useCallback(async (formData) => {
    const data = await authService.register(formData)
    return data
  }, [])

  // ── Logout ────────────────────────────────────────────────────────────────
  const logout = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) await authService.logout(refreshToken)
    } catch {
      // Logout silently even if the server call fails
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      setIsAuthenticated(false)
    }
  }, [])

  // ── Update user state ─────────────────────────────────────────────────────
  const updateUser = useCallback((updatedUser) => {
    setUser((prev) => ({ ...prev, ...updatedUser }))
  }, [])

  // ── Refresh user from API ─────────────────────────────────────────────────
  const refreshUser = useCallback(async () => {
    try {
      const profile = await authService.getMe()
      setUser(profile)
      return profile
    } catch {
      return null
    }
  }, [])

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    updateUser,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>')
  return ctx
}
