/**
 * 地理位置服务
 * 处理用户地理位置获取
 */
import { ref } from 'vue'

export function useGeolocation() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const coordinates = ref<{ latitude: number; longitude: number } | null>(null)

  /**
   * 获取用户当前位置
   */
  async function getCurrentPosition(): Promise<string | null> {
    if (!navigator.geolocation) {
      error.value = '浏览器不支持地理位置获取'
      return null
    }

    isLoading.value = true
    error.value = null

    return new Promise((resolve) => {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords
          coordinates.value = { latitude, longitude }
          
          // 返回QWeather API需要的格式：经度,纬度
          const locationQuery = `${longitude},${latitude}`
          
          isLoading.value = false
          console.log('✅ 地理位置获取成功:', { latitude, longitude })
          resolve(locationQuery)
        },
        (err) => {
          isLoading.value = false
          
          switch (err.code) {
            case err.PERMISSION_DENIED:
              error.value = '用户拒绝了地理位置访问请求'
              break
            case err.POSITION_UNAVAILABLE:
              error.value = '地理位置信息不可用'
              break
            case err.TIMEOUT:
              error.value = '获取地理位置超时'
              break
            default:
              error.value = '获取地理位置时发生未知错误'
              break
          }
          
          console.log('❌ 地理位置获取失败:', error.value)
          resolve(null)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 300000 // 5分钟内的缓存有效
        }
      )
    })
  }

  return {
    isLoading,
    error,
    coordinates,
    getCurrentPosition
  }
}
