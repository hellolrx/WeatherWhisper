import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export type FavoriteCity = {
  id: string
  name: string
  adm1?: string // 省份
  adm2?: string // 市级行政区
}

export type FavoriteCityResponse = {
  id: string
  city_name: string
  province?: string
  country?: string
  created_at: string
}

const API_BASE = 'http://127.0.0.1:8000/api'

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    list: [] as FavoriteCity[],
    limit: 10,
    loading: false,
    error: null as string | null,
  }),
  
  getters: {
    isAuthenticated: () => {
      const authStore = useAuthStore()
      return authStore.isAuthenticated
    },
    
    hasReachedLimit(): boolean {
      return this.list.length >= this.limit
    },
    
    canAddFavorite(): (cityId: string) => boolean {
      return (cityId: string) => {
        return !this.list.find(c => c.id === cityId) && !this.hasReachedLimit
      }
    }
  },
  
  actions: {
    // 从后端加载用户收藏
    async loadFavorites() {
      if (!this.isAuthenticated) {
        this.list = []
        return
      }
      
      try {
        this.loading = true
        this.error = null
        
        const authStore = useAuthStore()
        const response = await fetch(`${API_BASE}/favorites/list`, {
          headers: {
            'Authorization': authStore.getAuthHeader() || '',
          },
        })
        
        if (response.ok) {
          const data: FavoriteCityResponse[] = await response.json()
          // 转换数据格式以匹配前端期望
          this.list = data.map(item => ({
            id: item.id,
            name: item.city_name,
            adm1: item.province,
            adm2: item.country
          }))
        } else {
          throw new Error('加载收藏失败')
        }
      } catch (err) {
        console.error('加载收藏失败:', err)
        this.error = '加载收藏失败'
        this.list = []
      } finally {
        this.loading = false
      }
    },
    
    // 添加收藏
    async add(city: FavoriteCity) {
      if (!this.isAuthenticated) {
        this.error = '请先登录'
        return false
      }
      
      if (this.hasReachedLimit) {
        this.error = '收藏数量已达上限'
        return false
      }
      
      if (this.list.find(c => c.id === city.id)) {
        this.error = '该城市已在收藏中'
        return false
      }
      
      try {
        this.loading = true
        this.error = null
        
        const authStore = useAuthStore()
        const response = await fetch(`${API_BASE}/favorites/add`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': authStore.getAuthHeader() || '',
          },
          body: JSON.stringify({
            city_name: city.name,
            province: city.adm1,
            country: city.adm2
          }),
        })
        
        if (response.ok) {
          const data: FavoriteCityResponse = await response.json()
          // 添加到本地列表
          this.list.push({
            id: data.id,
            name: data.city_name,
            adm1: data.province,
            adm2: data.country
          })
          return true
        } else {
          const errorData = await response.json()
          throw new Error(errorData.detail || '添加收藏失败')
        }
      } catch (err) {
        console.error('添加收藏失败:', err)
        this.error = err instanceof Error ? err.message : '添加收藏失败'
        return false
      } finally {
        this.loading = false
      }
    },
    
    // 移除收藏
    async remove(id: string) {
      if (!this.isAuthenticated) {
        this.error = '请先登录'
        return false
      }
      
      try {
        this.loading = true
        this.error = null
        
        const city = this.list.find(c => c.id === id)
        if (!city) {
          this.error = '收藏不存在'
          return false
        }
        
        const authStore = useAuthStore()
        const response = await fetch(`${API_BASE}/favorites/remove/${encodeURIComponent(city.name)}?province=${encodeURIComponent(city.adm1 || '')}`, {
          method: 'DELETE',
          headers: {
            'Authorization': authStore.getAuthHeader() || '',
          },
        })
        
        if (response.ok) {
          // 从本地列表移除
          this.list = this.list.filter(c => c.id !== id)
          return true
        } else {
          throw new Error('移除收藏失败')
        }
      } catch (err) {
        console.error('移除收藏失败:', err)
        this.error = '移除收藏失败'
        return false
      } finally {
        this.loading = false
      }
    },
    
    // 清空收藏
    async clear() {
      if (!this.isAuthenticated) {
        this.error = '请先登录'
        return false
      }
      
      try {
        this.loading = true
        this.error = null
        
        // 逐个移除所有收藏
        const removePromises = this.list.map(city => this.remove(city.id))
        await Promise.all(removePromises)
        
        return true
      } catch (err) {
        console.error('清空收藏失败:', err)
        this.error = '清空收藏失败'
        return false
      } finally {
        this.loading = false
      }
    },
    
    // 清除错误
    clearError() {
      this.error = null
    },
    
    // 初始化收藏（在用户登录后调用）
    async init() {
      if (this.isAuthenticated) {
        await this.loadFavorites()
      } else {
        this.list = []
      }
    }
  },
})


