<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFavoritesStore } from '../stores/favorites'
import { useWeatherApi } from '../composables/useWeatherApi'
import { useGeolocation } from '../composables/useGeolocation'

// 组件导入
import SearchBox from '../components/search/SearchBox.vue'
import FavoriteCities from '../components/favorites/FavoriteCities.vue'
import CurrentWeather from '../components/weather/CurrentWeather.vue'
import HourlyForecast from '../components/weather/HourlyForecast.vue'
import DailyForecast from '../components/weather/DailyForecast.vue'

// 类型导入
import type { CityOption, CurrentWeather as CurrentWeatherType, HourlyWeather, DailyWeather, FavoriteCity } from '../types/weather'

// 状态管理
const favorites = useFavoritesStore()
const { loading, errorMsg, searchCities, getWeatherData } = useWeatherApi()
const { getCurrentPosition } = useGeolocation()

// 本地状态
const options = ref<CityOption[]>([])
const selectedCity = ref<CityOption | null>(null)
const currentWeather = ref<CurrentWeatherType | null>(null)
const hourlyData = ref<HourlyWeather[]>([])
const dailyData = ref<DailyWeather[]>([])
const showOptions = ref(false)

// 搜索相关方法
async function handleSearch(query: string) {
  const cities = await searchCities(query)
  options.value = cities
  
  if (cities.length === 1) {
    // 只有一个结果，直接加载
    await handleSelectCity(cities[0])
    showOptions.value = false
  } else if (cities.length > 1) {
    // 多个结果，显示选项
    showOptions.value = true
    // 如果有省会或主要城市，自动选择
    const mainCity = cities.find((c: CityOption) => c.adm2 === c.name) || cities[0]
    await handleSelectCity(mainCity)
  } else {
    errorMsg.value = '未找到匹配城市，请换个关键词试试'
    showOptions.value = false
  }
}

async function handleInput(query: string) {
  if (!query.trim()) {
    options.value = []
    showOptions.value = false
    return
  }
  await handleSearch(query)
}

async function handleSelectCity(city: CityOption) {
  selectedCity.value = city
  showOptions.value = false
  
  try {
    const weatherData = await getWeatherData(city.id)
    currentWeather.value = weatherData.current
    hourlyData.value = weatherData.hourly
    dailyData.value = weatherData.daily
  } catch (error) {
    console.error('获取天气数据失败:', error)
  }
}

function handleCloseOptions() {
  showOptions.value = false
}

// 收藏相关方法
function handleAddFavorite(city: CityOption) {
  favorites.add({
    id: city.id,
    name: city.name,
    adm1: city.adm1,
    adm2: city.adm2
  })
}

function handleRemoveFavorite(id: string) {
  favorites.remove(id)
}

async function handleLoadWeather(city: FavoriteCity) {
  await handleSelectCity(city as CityOption)
}

// 初始化
onMounted(async () => {
  // 尝试获取地理位置
  const locationQuery = await getCurrentPosition()
  if (locationQuery) {
    await handleSearch(locationQuery)
  }
})
</script>

<template>
  <div class="app">
    <div class="container">
      <!-- 标题区域 -->
      <header class="header">
        <h1 class="title">
          <span class="icon">🌤️</span>
          天语 · Weather Whisper
        </h1>
        <p class="subtitle">简洁纯净的天气查询</p>
      </header>

      <!-- 主布局 -->
      <div class="weather-app">
        <!-- 侧边栏：搜索和收藏 -->
        <aside class="sidebar">
          <!-- 搜索组件 -->
          <SearchBox
            :loading="loading"
            :options="options"
            :show-options="showOptions"
            :error-msg="errorMsg"
            @search="handleSearch"
            @select-city="handleSelectCity"
            @input="handleInput"
            @close-options="handleCloseOptions"
          />

          <!-- 收藏城市组件 -->
          <FavoriteCities
            :favorites="favorites.list"
            :limit="favorites.limit"
            :selected-city="selectedCity"
            :show-options="showOptions"
            :options-length="options.length"
            @load-weather="handleLoadWeather"
            @remove-favorite="handleRemoveFavorite"
            @add-favorite="handleAddFavorite"
          />
        </aside>

        <!-- 主要内容：天气信息 -->
        <main class="main-content">
          <div v-if="currentWeather && selectedCity" class="weather-section">
            <!-- 当前天气组件 -->
            <CurrentWeather
              :weather="currentWeather"
              :selected-city="selectedCity"
            />

            <!-- 预报容器 -->
            <div class="forecast-container">
              <!-- 24小时预报组件 -->
              <HourlyForecast :hourly-data="hourlyData" />

              <!-- 7天预报组件 -->
              <DailyForecast :daily-data="dailyData" />
            </div>
          </div>
        </main>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading && !currentWeather" class="loading-state">
        <div class="loading-spinner">🌀</div>
        <p>正在获取天气信息...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 导入样式模块 */
@import '../styles/global.css';
@import '../styles/layout.css';
@import '../styles/cards.css';
</style>
