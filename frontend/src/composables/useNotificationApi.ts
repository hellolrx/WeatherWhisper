import { ref } from 'vue'
import http from '../utils/http'
import { useAuthStore } from '../stores/auth'

export type SendWeatherPayload = {
  city_id?: string
  city_name?: string
  province?: string
  email?: string
  dry_run?: boolean
}

export type ScheduleWeatherPayload = {
  city_id?: string
  city_name?: string
  province?: string
  email?: string
  type: 'ONCE'|'DAILY'
  time?: string
  date?: string
  timezone?: string
}

export function useNotificationApi() {
  const sending = ref(false)
  const error = ref<string | null>(null)
  const auth = useAuthStore()

  function authHeader() {
    const h = auth.getAuthHeader()
    return h ? { Authorization: h } : {}
  }

  async function previewWeatherEmail(payload: SendWeatherPayload) {
    error.value = null
    const body = { ...payload, dry_run: true }
    const res = await http.post('notifications/send-weather', body, { headers: authHeader(), timeout: 45000 })
    return res.data
  }

  async function sendWeatherEmail(payload: SendWeatherPayload) {
    error.value = null
    sending.value = true
    try {
      const res = await http.post('notifications/send-weather', payload, { headers: authHeader(), timeout: 45000 })
      return res.data
    } finally {
      sending.value = false
    }
  }

  async function scheduleWeatherEmail(payload: ScheduleWeatherPayload) {
    error.value = null
    sending.value = true
    try {
      const finalPayload = { time: '09:00', timezone: 'Asia/Shanghai', ...payload }
      const res = await http.post('notifications/schedule-weather', finalPayload, { headers: authHeader(), timeout: 45000 })
      return res.data
    } finally {
      sending.value = false
    }
  }

  return { sending, error, previewWeatherEmail, sendWeatherEmail, scheduleWeatherEmail }
}
