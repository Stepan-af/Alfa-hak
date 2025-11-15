import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User, LoginRequest, TokenRequest, UpdateProfileRequest } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const userEmail = computed(() => user.value?.email || '')
  const userName = computed(() => user.value?.full_name || user.value?.email || 'User')

  // Actions
  const loginWithMagicLink = async (email: string): Promise<boolean> => {
    try {
      loading.value = true
      error.value = null

      const data: LoginRequest = { email }
      await authApi.loginMagic(data)
      
      return true
    } catch (err: any) {
      error.value = err?.detail || 'Failed to send magic link'
      return false
    } finally {
      loading.value = false
    }
  }

  const loginWithToken = async (token: string): Promise<boolean> => {
    try {
      loading.value = true
      error.value = null

      const data: TokenRequest = { token }
      const response = await authApi.getToken(data)

      // Save tokens
      accessToken.value = response.access_token
      refreshToken.value = response.refresh_token
      user.value = response.user

      // Store in localStorage
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)

      return true
    } catch (err: any) {
      error.value = err?.detail || 'Invalid or expired token'
      return false
    } finally {
      loading.value = false
    }
  }

  const checkAuth = async (): Promise<boolean> => {
    try {
      // Check if tokens exist
      const storedAccessToken = localStorage.getItem('access_token')
      const storedRefreshToken = localStorage.getItem('refresh_token')

      if (!storedAccessToken || !storedRefreshToken) {
        return false
      }

      accessToken.value = storedAccessToken
      refreshToken.value = storedRefreshToken

      // Fetch user profile
      const userData = await authApi.getMe()
      user.value = userData

      return true
    } catch (err: any) {
      // If auth check fails, clear tokens
      logout()
      return false
    }
  }

  const updateProfile = async (data: UpdateProfileRequest): Promise<boolean> => {
    try {
      loading.value = true
      error.value = null

      const updatedUser = await authApi.updateProfile(data)
      user.value = updatedUser

      return true
    } catch (err: any) {
      error.value = err?.detail || 'Failed to update profile'
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (err) {
      // Ignore logout errors
      console.error('Logout error:', err)
    } finally {
      // Clear state
      user.value = null
      accessToken.value = null
      refreshToken.value = null

      // Clear localStorage
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    user,
    accessToken,
    refreshToken,
    loading,
    error,
    
    // Getters
    isAuthenticated,
    userEmail,
    userName,
    
    // Actions
    loginWithMagicLink,
    loginWithToken,
    checkAuth,
    updateProfile,
    logout,
    clearError,
  }
})
