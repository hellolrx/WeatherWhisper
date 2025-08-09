<script setup lang="ts">
import { ref, onMounted } from 'vue'
import http from '../utils/http'
import { useFavoritesStore } from '../stores/favorites'

type CityOption = { id: string; name: string }

const query = ref('')
const options = ref<CityOption[]>([])
const selectedCity = ref<CityOption | null>(null)
const now = ref<any>(null)
const hourly = ref<any[]>([])
const daily = ref<any[]>([])
const loading = ref(false)
const errorMsg = ref('')

const favorites = useFavoritesStore()

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  errorMsg.value = ''
  try {
    console.log('[req] GET /api/geo', { query: query.value })
    const { data } = await http.get('/geo', { params: { query: query.value } })
    console.log('[res] /api/geo', data)
    options.value = (data.location || []).map((x: any) => ({ id: x.id, name: `${x.name}${x.adm2 ? ' · ' + x.adm2 : ''}` }))
    if (!options.value.length) {
      errorMsg.value = '未找到匹配城市，请换个关键词试试'
    }
  } catch (e: any) {
    console.error(e)
    errorMsg.value = e?.response?.data?.detail?.message || e?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

async function loadWeather(city: CityOption) {
  selectedCity.value = city
  loading.value = true
  errorMsg.value = ''
  try {
    console.log('[req] weather for', city)
    const [nowRes, hRes, dRes] = await Promise.all([
      http.get('/weather/now', { params: { location: city.id } }),
      http.get('/weather/24h', { params: { location: city.id } }),
      http.get('/weather/7d', { params: { location: city.id } }),
    ])
    now.value = nowRes.data
    hourly.value = hRes.data?.hourly || []
    daily.value = dRes.data?.daily || []
  } catch (e: any) {
    console.error(e)
    errorMsg.value = e?.response?.data?.detail?.message || e?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

function addFavorite() {
  if (!selectedCity.value) return
  favorites.add({ id: selectedCity.value.id, name: selectedCity.value.name })
}

onMounted(async () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(() => {}, () => {})
  }
})
</script>

<template>
  <div class="container">
    <h1>天语 · Weather Whisper</h1>
    <div class="search">
      <input v-model="query" placeholder="输入城市名，例如：北京" @keyup.enter="search" />
      <button @click="search" :disabled="loading">{{ loading ? '搜索中…' : '搜索' }}</button>
      <select v-if="options.length" @change="loadWeather(options[$event.target.selectedIndex])">
        <option v-for="opt in options" :key="opt.id">{{ opt.name }}</option>
      </select>
      <button :disabled="!selectedCity" @click="addFavorite">关注</button>
    </div>
    <p v-if="errorMsg" class="error">{{ errorMsg }}</p>

    <div class="favorites" v-if="favorites.list.length">
      <h3>已关注</h3>
      <div class="fav-list">
        <button v-for="c in favorites.list" :key="c.id" @click="loadWeather(c)">{{ c.name }}</button>
      </div>
    </div>

    <div class="weather" v-if="now">
      <h2>{{ selectedCity?.name }}</h2>
      <div class="now">当前温度：{{ now?.now?.temp }}℃ · {{ now?.now?.text }}</div>
      <div class="hourly">
        <h3>未来24小时</h3>
        <div class="scroll">
          <div v-for="h in hourly" :key="h.fxTime" class="card">{{ h.fxTime.slice(11,16) }}｜{{ h.temp }}℃</div>
        </div>
      </div>
      <div class="daily">
        <h3>未来7天</h3>
        <div class="grid">
          <div v-for="d in daily" :key="d.fxDate" class="card">{{ d.fxDate.slice(5) }}｜{{ d.tempMin }}~{{ d.tempMax }}℃</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container { max-width: 960px; margin: 20px auto; padding: 0 16px; }
.search { display: flex; gap: 8px; align-items: center; }
.error { color: #d93025; margin-top: 8px; }
.fav-list { display: flex; gap: 8px; flex-wrap: wrap; }
.weather { margin-top: 16px; }
.scroll { display: flex; gap: 8px; overflow-x: auto; padding: 8px 0; }
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; }
.card { border: 1px solid #eee; padding: 8px 12px; border-radius: 6px; background: #fafafa; }
input { flex: 1; padding: 8px; }
button { padding: 8px 12px; }
select { padding: 8px; }
</style>


