import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, TokenResponse, AuthState } from '../types/auth'

// 存储键名
const STORAGE_KEYS = {
  ACCESS_TOKEN: 'ww_access_token',
  REFRESH_TOKEN: 'ww_refresh_token',
  USER: 'ww_user',
  REMEMBER_ME: 'ww_remember_me'
}

// 从localStorage加载数据
function loadFromStorage<T>(key: string, defaultValue: T): T {
  try {
    const item = localStorage.getItem(key)
    return item ? JSON.parse(item) : defaultValue
  } catch {
    return defaultValue
  }
}

// 保存到localStorage
function saveToStorage<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.error(`保存到localStorage失败: ${key}`, error)
  }
}

// 从localStorage删除数据
function removeFromStorage(key: string): void {
  try {
    localStorage.removeItem(key)
  } catch (error) {
    console.error(`从localStorage删除失败: ${key}`, error)
  }
}

export const useAuthStore = defineStore('auth', () => {
  // 状态
  const user = ref<User | null>(loadFromStorage(STORAGE_KEYS.USER, null))
  const tokens = ref<TokenResponse | null>(null)
  const isLoading = ref(false)
  const isGuest = ref(false)

  // 计算属性
  const isAuthenticated = computed(() => !!user.value && !!tokens.value)
  const accessToken = computed(() => tokens.value?.access_token || null)
  const refreshToken = computed(() => tokens.value?.refresh_token || null)

  // 初始化令牌
  function initTokens() {
    const accessToken = loadFromStorage(STORAGE_KEYS.ACCESS_TOKEN, null)
    const refreshToken = loadFromStorage(STORAGE_KEYS.REFRESH_TOKEN, null)
    
    if (accessToken && refreshToken) {
      tokens.value = {
        access_token: accessToken,
        refresh_token: refreshToken,
        token_type: 'bearer',
        expires_in: 0 // 从localStorage加载时不关心过期时间
      }
    }
  }

  // 设置用户信息
  function setUser(userData: User) {
    user.value = userData
    saveToStorage(STORAGE_KEYS.USER, userData)
  }

  // 设置令牌
  function setTokens(tokenData: TokenResponse, rememberMe: boolean = false) {
    tokens.value = tokenData
    
    if (rememberMe) {
      saveToStorage(STORAGE_KEYS.ACCESS_TOKEN, tokenData.access_token)
      saveToStorage(STORAGE_KEYS.REFRESH_TOKEN, tokenData.refresh_token)
      saveToStorage(STORAGE_KEYS.REMEMBER_ME, true)
    } else {
      // 只在session中保存
      sessionStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, tokenData.access_token)
      sessionStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, tokenData.refresh_token)
    }
  }

  // 启用访客模式
  function enableGuestMode() {
    isGuest.value = true
    user.value = null
    tokens.value = null
    // 清除所有认证相关存储
    Object.values(STORAGE_KEYS).forEach(key => removeFromStorage(key))
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
  }

  // 用户登录
  function login(userData: User, tokenData: TokenResponse, rememberMe: boolean = false) {
    setUser(userData)
    setTokens(tokenData, rememberMe)
    isGuest.value = false
  }

  // 用户登出
  function logout() {
    user.value = null
    tokens.value = null
    isGuest.value = false
    isLoading.value = false
    
    // 清除所有认证相关存储
    Object.values(STORAGE_KEYS).forEach(key => removeFromStorage(key))
    sessionStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    sessionStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
  }

  // 更新令牌
  function updateTokens(tokenData: TokenResponse) {
    const rememberMe = loadFromStorage(STORAGE_KEYS.REMEMBER_ME, false)
    setTokens(tokenData, rememberMe)
  }

  // 设置加载状态
  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  // 检查令牌是否有效
  function hasValidToken(): boolean {
    return !!(tokens.value?.access_token)
  }

  // 获取认证头
  function getAuthHeader(): string | null {
    if (tokens.value?.access_token) {
      return `${tokens.value.token_type} ${tokens.value.access_token}`
    }
    return null
  }

  // 初始化认证状态
  function initAuth() {
    initTokens()
    
    // 如果有令牌但没有用户信息，尝试从localStorage恢复
    if (tokens.value && !user.value) {
      const savedUser = loadFromStorage(STORAGE_KEYS.USER, null)
      if (savedUser) {
        user.value = savedUser
      }
    }
  }

  return {
    // 状态
    user,
    tokens,
    isLoading,
    isGuest,
    
    // 计算属性
    isAuthenticated,
    accessToken,
    refreshToken,
    
    // 方法
    setUser,
    setTokens,
    enableGuestMode,
    login,
    logout,
    updateTokens,
    setLoading,
    hasValidToken,
    getAuthHeader,
    initAuth
  }
}) 