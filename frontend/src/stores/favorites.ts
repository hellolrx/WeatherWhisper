import { defineStore } from 'pinia'

export type FavoriteCity = {
  id: string
  name: string
  adm1?: string // 省份
  adm2?: string // 市级行政区
}

const STORAGE_KEY = 'ww_favorites'

function loadFromStorage(): FavoriteCity[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveToStorage(list: FavoriteCity[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

export const useFavoritesStore = defineStore('favorites', {
  state: () => ({
    list: loadFromStorage() as FavoriteCity[],
    limit: 10,
  }),
  actions: {
    add(city: FavoriteCity) {
      if (this.list.find(c => c.id === city.id)) return
      if (this.list.length >= this.limit) return
      this.list.push(city)
      saveToStorage(this.list)
    },
    remove(id: string) {
      this.list = this.list.filter(c => c.id !== id)
      saveToStorage(this.list)
    },
    clear() {
      this.list = []
      saveToStorage(this.list)
    },
  },
})


