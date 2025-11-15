import apiClient from './client'
import type { 
  LoginRequest, 
  LoginResponse, 
  TokenRequest, 
  TokenResponse,
  UpdateProfileRequest,
  User 
} from '@/types/auth'

export const authApi = {
  // Send magic link to email
  loginMagic: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/auth/login_magic', data)
    return response.data
  },

  // Exchange magic token for JWT
  getToken: async (data: TokenRequest): Promise<TokenResponse> => {
    const response = await apiClient.post<TokenResponse>('/auth/token', data)
    return response.data
  },

  // Get current user profile
  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/users/me')
    return response.data
  },

  // Update user profile
  updateProfile: async (data: UpdateProfileRequest): Promise<User> => {
    const response = await apiClient.post<User>('/auth/users/update', data)
    return response.data
  },

  // Logout
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout')
  },
}
