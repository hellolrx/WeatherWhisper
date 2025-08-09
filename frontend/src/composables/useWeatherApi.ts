/**
 * 天气API服务层
 * 封装所有天气相关的API调用
 */
import { ref } from 'vue'
import http from '../utils/http'
import type { CityOption, CurrentWeather, HourlyWeather, DailyWeather } from '../types/weather'

export function useWeatherApi() {
  const loading = ref(false)
  const errorMsg = ref('')

  /**
   * 搜索城市
   */
  async function searchCities(query: string): Promise<CityOption[]> {
    if (!query.trim()) return []
    
    loading.value = true
    errorMsg.value = ''
    
    try {
      console.log('[req] GET /api/geo', { query })
      const { data } = await http.get('/geo', { params: { query } })
      console.log('[res] /api/geo', data)
      
      const cities = (data.location || []).map((x: any) => ({
        id: x.id,
        name: x.name,
        adm1: x.adm1,
        adm2: x.adm2,
        fullName: `${x.name}${x.adm2 && x.adm2 !== x.name ? ' · ' + x.adm2 : ''}${x.adm1 && x.adm1 !== x.adm2 ? ' · ' + x.adm1 : ''}`
      }))
      
      return cities
    } catch (e: any) {
      console.error(e)
      errorMsg.value = e?.response?.data?.detail?.message || e?.message || '搜索失败'
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 获取天气数据
   */
  async function getWeatherData(cityId: string) {
    loading.value = true
    errorMsg.value = ''
    
    try {
      console.log('[req] weather for city:', cityId)
      const [nowRes, hRes, dRes] = await Promise.all([
        http.get('/weather/now', { params: { location: cityId } }),
        http.get('/weather/24h', { params: { location: cityId } }),
        http.get('/weather/7d', { params: { location: cityId } }),
      ])
      
      const currentWeather: CurrentWeather = nowRes.data
      const hourlyWeather: HourlyWeather[] = hRes.data?.hourly?.slice(0, 24) || []
      const dailyWeather: DailyWeather[] = dRes.data?.daily || []
      
      // 调试信息
      console.log('📊 天气数据加载完成:')
      console.log('当前天气:', currentWeather)
      console.log('24小时预报数量:', hourlyWeather.length)
      console.log('7天预报数量:', dailyWeather.length)
      
      return {
        current: currentWeather,
        hourly: hourlyWeather,
        daily: dailyWeather
      }
    } catch (e: any) {
      console.error(e)
      errorMsg.value = e?.response?.data?.detail?.message || e?.message || '获取天气数据失败'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    errorMsg,
    searchCities,
    getWeatherData
  }
}
