// 用户基础信息
export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login?: string
}

// 用户注册请求
export interface UserCreate {
  email: string
  username: string
  password: string
}

// 用户登录请求
export interface UserLogin {
  email: string
  password: string
  remember_me: boolean
}

// 令牌响应
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

// 登录响应
export interface LoginResponse {
  success: boolean
  message: string
  remaining_attempts?: number
  locked_until?: string
  user?: User
  tokens?: TokenResponse
}

// 注册响应
export interface RegisterResponse {
  success: boolean
  message: string
  user?: {
    id: number
    email: string
    username: string
  }
}

// 访客模式信息
export interface GuestModeInfo {
  success: boolean
  message: string
  features: {
    weather_search: boolean
    weather_display: boolean
    favorites: boolean
    user_profile: boolean
  }
}

// 认证状态
export interface AuthState {
  user: User | null
  tokens: TokenResponse | null
  isAuthenticated: boolean
  isGuest: boolean
  isLoading: boolean
}

// 表单验证错误
export interface FormErrors {
  email?: string
  username?: string
  password?: string
  confirmPassword?: string
  general?: string
} 