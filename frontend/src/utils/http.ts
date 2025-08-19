import axios from 'axios'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

function readAccessToken(): string | null {
  const ls = window.localStorage.getItem('ww_access_token')
  const ss = window.sessionStorage.getItem('ww_access_token')
  const raw = ls ?? ss
  if (!raw) return null
  try {
    const parsed = JSON.parse(raw)
    return typeof parsed === 'string' ? parsed : null
  } catch {
    return raw
  }
}

http.interceptors.request.use((config) => {
  try {
    const url = (config.url || '').replace(/^\/+/, '')
    // 跳过 Auth 相关端点
    if (url.startsWith('auth/')) return config

    const token = readAccessToken()
    if (token) {
      config.headers = config.headers || {}
      if (!(config.headers as any)['Authorization']) {
        ;(config.headers as any)['Authorization'] = `Bearer ${token}`
      }
    }
  } catch {}
  return config
})

export default http


