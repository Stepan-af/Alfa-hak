// User types
export interface User {
  id: string
  email: string
  full_name: string | null
  phone: string | null
  business_type: string | null
  is_active: boolean
  created_at: string
}

// Auth types
export interface LoginRequest {
  email: string
}

export interface LoginResponse {
  message: string
}

export interface TokenRequest {
  token: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface UpdateProfileRequest {
  full_name?: string
  phone?: string
  business_type?: string
}

// API Error
export interface ApiError {
  detail: string
}
