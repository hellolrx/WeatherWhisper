import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import type { UserCreate, UserLogin, LoginResponse, RegisterResponse } from '../types/auth'

// API基础URL
const API_BASE = 'http://127.0.0.1:8000/api'

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()
  
  // 响应式状态
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const formErrors = reactive<Record<string, string>>({})

  // 清除错误
  function clearErrors() {
    error.value = null
    Object.keys(formErrors).forEach(key => {
      formErrors[key] = ''
    })
  }

  // 设置错误
  function setError(message: string, field?: string) {
    if (field) {
      formErrors[field] = message
    } else {
      error.value = message
    }
  }

  // 用户注册
  async function register(userData: UserCreate): Promise<boolean> {
    try {
      clearErrors()
      isLoading.value = true
      
      const response = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      const data: RegisterResponse = await response.json()

      if (!response.ok) {
        if (data.message) {
          setError(data.message)
        } else {
          setError('注册失败，请稍后重试')
        }
        return false
      }

      if (data.success) {
        // 注册成功，跳转到登录页
        router.push('/login')
        return true
      } else {
        setError(data.message || '注册失败')
        return false
      }

    } catch (err) {
      console.error('注册失败:', err)
      setError('网络错误，请检查网络连接')
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 用户登录
  async function login(userData: UserLogin): Promise<boolean> {
    try {
      clearErrors()
      isLoading.value = true
      
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      const data: LoginResponse = await response.json()

      if (!response.ok) {
        if (data.message) {
          setError(data.message)
        } else {
          setError('登录失败，请稍后重试')
        }
        return false
      }

      if (data.success && data.user && data.tokens) {
        // 登录成功，保存用户信息和令牌
        authStore.login(data.user, data.tokens, userData.remember_me)
        
        // 跳转到天气主页
        router.push('/')
        return true
      } else {
        // 登录失败，显示具体错误信息
        if (data.remaining_attempts !== undefined) {
          setError(`${data.message}，剩余尝试次数: ${data.remaining_attempts}`)
        } else {
          setError(data.message || '登录失败')
        }
        return false
      }

    } catch (err) {
      console.error('登录失败:', err)
      setError('网络错误，请检查网络连接')
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 用户登出
  async function logout(): Promise<void> {
    try {
      // 调用后端登出接口（可选）
      if (authStore.hasValidToken()) {
        await fetch(`${API_BASE}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': authStore.getAuthHeader() || '',
          },
        }).catch(() => {
          // 忽略登出接口错误
        })
      }
    } catch (err) {
      console.error('登出接口调用失败:', err)
    } finally {
      // 清除本地状态
      authStore.logout()
      router.push('/login')
    }
  }

  // 启用访客模式
  function enableGuestMode(): void {
    authStore.enableGuestMode()
    router.push('/')
  }

  // 刷新令牌
  async function refreshToken(): Promise<boolean> {
    try {
      if (!authStore.refreshToken) {
        return false
      }

      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: authStore.refreshToken,
        }),
      })

      if (response.ok) {
        const tokens = await response.json()
        authStore.updateTokens(tokens)
        return true
      }

      return false
    } catch (err) {
      console.error('令牌刷新失败:', err)
      return false
    }
  }

  // 获取用户资料
  async function getUserProfile(): Promise<boolean> {
    try {
      if (!authStore.hasValidToken()) {
        return false
      }

      const response = await fetch(`${API_BASE}/auth/profile`, {
        headers: {
          'Authorization': authStore.getAuthHeader() || '',
        },
      })

      if (response.ok) {
        const user = await response.json()
        authStore.setUser(user)
        return true
      }

      return false
    } catch (err) {
      console.error('获取用户资料失败:', err)
      return false
    }
  }

  // 表单验证
  function validateForm(formData: Record<string, any>, rules: Record<string, (value: any) => string | null>): boolean {
    clearErrors()
    let isValid = true

    Object.keys(rules).forEach(field => {
      const value = formData[field]
      const rule = rules[field]
      const error = rule(value)
      
      if (error) {
        formErrors[field] = error
        isValid = false
      }
    })

    return isValid
  }

  // 登录表单验证规则
  const loginValidationRules = {
    email: (value: string) => {
      if (!value) return '请输入邮箱'
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '请输入有效的邮箱地址'
      return null
    },
    password: (value: string) => {
      if (!value) return '请输入密码'
      if (value.length < 8) return '密码长度至少8位'
      return null
    }
  }

  // 注册表单验证规则
  const registerValidationRules = {
    email: (value: string) => {
      if (!value) return '请输入邮箱'
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return '请输入有效的邮箱地址'
      return null
    },
    username: (value: string) => {
      if (!value) return '请输入用户名'
      if (value.length < 2) return '用户名长度至少2位'
      if (value.length > 50) return '用户名长度不能超过50位'
      return null
    },
    password: (value: string) => {
      if (!value) return '请输入密码'
      if (value.length < 8) return '密码长度至少8位'
      return null
    },
    confirmPassword: (value: string, formData: Record<string, any>) => {
      if (!value) return '请确认密码'
      if (value !== formData.password) return '两次输入的密码不一致'
      return null
    }
  }

  return {
    // 状态
    isLoading,
    error,
    formErrors,
    
    // 方法
    register,
    login,
    logout,
    enableGuestMode,
    refreshToken,
    getUserProfile,
    validateForm,
    clearErrors,
    setError,
    
    // 验证规则
    loginValidationRules,
    registerValidationRules
  }
} 