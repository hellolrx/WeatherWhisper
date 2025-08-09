<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onBeforeUnmount } from 'vue'
import http from '../utils/http'
import { useFavoritesStore } from '../stores/favorites'

type CityOption = { id: string; name: string; adm1?: string; adm2?: string; fullName?: string }

const query = ref('')
const options = ref<CityOption[]>([])
const selectedCity = ref<CityOption | null>(null)
const now = ref<any>(null)
const hourly = ref<any[]>([])
const daily = ref<any[]>([])
const loading = ref(false)
const errorMsg = ref('')
const showOptions = ref(false)
const searchTimeout = ref<number | null>(null)
const showFullHourly = ref(false) // 控制24小时预报展开状态

const favorites = useFavoritesStore()

// 鼠标拖拽滚动功能
function addDragScrolling(element: HTMLElement) {
  let isDown = false
  let startX: number
  let scrollLeft: number
  let hasMoved = false

  element.addEventListener('mousedown', (e) => {
    isDown = true
    hasMoved = false
    element.classList.add('dragging')
    startX = e.pageX - element.offsetLeft
    scrollLeft = element.scrollLeft
    e.preventDefault()
  })

  element.addEventListener('mouseleave', () => {
    isDown = false
    element.classList.remove('dragging')
  })

  element.addEventListener('mouseup', () => {
    isDown = false
    element.classList.remove('dragging')
  })

  element.addEventListener('mousemove', (e) => {
    if (!isDown) return
    e.preventDefault()
    hasMoved = true
    const x = e.pageX - element.offsetLeft
    const walk = (x - startX) * 2 // 滚动速度
    element.scrollLeft = scrollLeft - walk
  })

  // 防止拖拽时触发点击事件
  element.addEventListener('click', (e) => {
    if (hasMoved) {
      e.preventDefault()
      e.stopPropagation()
    }
  })
}

// 初始化所有小时预报容器的拖拽功能
function initializeDragScrolling() {
  nextTick(() => {
    const hourlyContainers = document.querySelectorAll('.hourly-forecast-module')
    hourlyContainers.forEach((container) => {
      const element = container as HTMLElement
      element.style.cursor = 'grab'
      addDragScrolling(element)
    })
  })
}

// 防抖搜索
async function handleInput() {
  if (searchTimeout.value) clearTimeout(searchTimeout.value)
  if (!query.value.trim()) {
    options.value = []
    showOptions.value = false
    return
  }
  
  searchTimeout.value = setTimeout(async () => {
    await search()
  }, 500)
}

async function search() {
  if (!query.value.trim()) return
  loading.value = true
  errorMsg.value = ''
  try {
    console.log('[req] GET /api/geo', { query: query.value })
    const { data } = await http.get('/geo', { params: { query: query.value } })
    console.log('[res] /api/geo', data)
    
    const cities = (data.location || []).map((x: any) => ({
      id: x.id,
      name: x.name,
      adm1: x.adm1,
      adm2: x.adm2,
      fullName: `${x.name}${x.adm2 && x.adm2 !== x.name ? ' · ' + x.adm2 : ''}${x.adm1 && x.adm1 !== x.adm2 ? ' · ' + x.adm1 : ''}`
    }))
    
    options.value = cities
    
    if (cities.length === 1) {
      // 只有一个结果，直接加载
      await loadWeather(cities[0])
      showOptions.value = false
    } else if (cities.length > 1) {
      // 多个结果，显示选项
      showOptions.value = true
      // 如果有省会或主要城市，自动选择
      const mainCity = cities.find((c: CityOption) => c.adm2 === c.name) || cities[0]
      await loadWeather(mainCity)
    } else {
      errorMsg.value = '未找到匹配城市，请换个关键词试试'
      showOptions.value = false
    }
  } catch (e: any) {
    console.error(e)
    errorMsg.value = e?.response?.data?.detail?.message || e?.message || '请求失败'
    showOptions.value = false
  } finally {
    loading.value = false
  }
}

async function selectCity(city: CityOption) {
  query.value = city.name
  showOptions.value = false
  await loadWeather(city)
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
    hourly.value = hRes.data?.hourly?.slice(0, 24) || []  // 显示全部24小时
    daily.value = dRes.data?.daily || []
    
    // 调试信息
    console.log('📊 天气数据加载完成:')
    console.log('当前天气:', now.value)
    console.log('24小时预报数量:', hourly.value.length)
    console.log('7天预报数量:', daily.value.length)
    console.log('7天预报数据:', daily.value)
    
    // 初始化拖拽滚动功能
    initializeDragScrolling()
  } catch (e: any) {
    console.error(e)
    errorMsg.value = e?.response?.data?.detail?.message || e?.message || '请求失败'
  } finally {
    loading.value = false
  }
}

function addFavorite() {
  if (!selectedCity.value) return
  favorites.add({ 
    id: selectedCity.value.id, 
    name: selectedCity.value.name,
    adm1: selectedCity.value.adm1,
    adm2: selectedCity.value.adm2
  })
}

function removeFavorite(id: string) {
  favorites.remove(id)
}

// 天气图标映射
function getWeatherIcon(iconCode: string): string {
  const iconMap: Record<string, string> = {
    '100': '☀️', '101': '🌤️', '102': '⛅', '103': '🌥️', '104': '☁️',
    '200': '🌫️', '201': '🌫️', '202': '🌫️', '203': '🌫️', '204': '🌫️',
    '300': '🌦️', '301': '🌧️', '302': '⛈️', '303': '⛈️', '304': '⛈️',
    '305': '🌧️', '306': '🌧️', '307': '🌧️', '308': '🌧️', '309': '🌦️',
    '310': '🌦️', '311': '🌦️', '312': '🌦️', '313': '🌦️', '314': '🌦️',
    '315': '🌦️', '316': '🌦️', '317': '🌦️', '318': '🌦️', '399': '🌧️',
    '400': '🌨️', '401': '🌨️', '402': '❄️', '403': '❄️', '404': '🌨️',
    '405': '🌨️', '406': '🌨️', '407': '❄️', '408': '❄️', '409': '🌨️',
    '410': '🌨️', '499': '❄️', '500': '🌫️', '501': '🌫️', '502': '🌫️',
    '503': '🌪️', '504': '🌪️', '507': '🌪️', '508': '🌪️', '900': '🌡️',
    '901': '🌡️', '999': '❓'
  }
  return iconMap[iconCode] || '🌤️'
}

// 根据时间判断是白天还是夜晚
function isDayTime(): boolean {
  const hour = new Date().getHours()
  return hour >= 6 && hour < 18
}

const canAddFavorite = computed(() => {
  return selectedCity.value && 
         !favorites.list.find(c => c.id === selectedCity.value?.id) &&
         favorites.list.length < favorites.limit
})

// 计算显示的小时数据
const displayedHourly = computed(() => {
  if (showFullHourly.value) {
    return hourly.value // 显示全部24小时
  } else {
    return hourly.value.slice(0, 12) // 只显示前12小时
  }
})

// 切换展开状态
function toggleHourlyExpand() {
  showFullHourly.value = !showFullHourly.value
}

// 计算按省份分组的收藏城市
const favoritesByProvince = computed(() => {
  const grouped: Record<string, typeof favorites.list> = {}
  favorites.list.forEach(city => {
    const province = city.adm1 || '其他'
    if (!grouped[province]) {
      grouped[province] = []
    }
    grouped[province].push(city)
  })
  return grouped
})

// 关闭下拉选项
function closeOptions() {
  showOptions.value = false
}

onMounted(async () => {
  // 尝试获取地理位置
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords
        query.value = `${longitude},${latitude}`
        await search()
      },
      () => {
        console.log('地理位置获取失败，使用搜索功能')
      }
    )
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

      <!-- 全新的稳健布局结构 -->
      <div class="weather-app">
        <!-- 侧边栏：搜索和收藏 -->
        <aside class="sidebar">
          <!-- 搜索区域 -->
          <div class="search-section">
            <div class="search-header">
              <h3 class="search-title">🔍 搜索城市</h3>
            </div>
            
            <div class="search-bar">
              <div class="input-wrapper">
                <input 
                  v-model="query" 
                  placeholder="输入城市名，例如：北京" 
                  @input="handleInput"
                  @keyup.enter="search"
                  @focus="showOptions = options.length > 1"             
                  class="search-input"
                />
                <button 
                  @click="search" 
                  :disabled="loading" 
                  class="search-btn"
                >
                  <span v-if="loading">🔄</span>
                  <span v-else>🔍</span>
                </button>
              </div>
              
                      <!-- 搜索结果下拉 - 使用绝对定位避免影响布局流 -->
        <Transition name="dropdown">
          <div v-if="showOptions && options.length > 1" class="options-dropdown">
            <div class="dropdown-header">
              <span>选择城市</span>
              <button @click="closeOptions" class="close-btn">✕</button>
            </div>
            <div 
              v-for="opt in options" 
              :key="opt.id" 
              @click="selectCity(opt)"
              class="option-item"
            >
              📍 {{ opt.fullName }}
            </div>
          </div>
        </Transition>
            </div>

            <!-- 关注按钮 -->
            <button 
              v-if="selectedCity" 
              @click="addFavorite" 
              :disabled="!canAddFavorite"
              class="favorite-btn"
              :class="{ 'disabled': !canAddFavorite }"
            >
              {{ canAddFavorite ? '⭐ 关注' : '✅ 已关注' }}
            </button>
          </div>

          <!-- 错误提示 -->
          <div v-if="errorMsg" class="error-message">
            ⚠️ {{ errorMsg }}
          </div>

                <!-- 收藏城市 - 添加动态间距适应搜索下拉框 -->
      <Transition name="favorites">
        <div v-if="favorites.list.length" class="favorites-section" :class="{ 'pushed-down': showOptions && options.length > 1 }">
          <div class="favorites-header">
            <h3 class="section-title">📌 已关注的城市</h3>
            <span class="favorites-count">{{ favorites.list.length }}/{{ favorites.limit }}</span>
          </div>
          
          <!-- 按省份分组显示 -->
          <div class="favorites-by-province">
            <div 
              v-for="(cities, province) in favoritesByProvince" 
              :key="province"
              class="province-group"
            >
              <div class="province-header">
                <span class="province-name">{{ province }}</span>
                <span class="province-count">({{ cities.length }})</span>
              </div>
              <div class="province-cities">
                <div 
                  v-for="city in cities" 
                  :key="city.id" 
                  class="favorite-card"
                  @click="loadWeather(city)"
                >
                  <span class="city-name">{{ city.name }}</span>
                  <button 
                    @click.stop="removeFavorite(city.id)"
                    class="remove-btn"
                    title="移除关注"
                  >
                    ❌
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
        </aside>

        <!-- 主要内容：天气信息 -->
        <main class="main-content">
          <!-- 天气信息 -->
          <div v-if="now && selectedCity" class="weather-section">
            <!-- 当前天气 -->
            <div class="current-weather">
              <div class="current-header">
                <h2 class="city-name">📍 {{ selectedCity.name }}</h2>
                <div class="update-time">
                  更新时间：{{ new Date(now.updateTime).toLocaleString() }}
                </div>
              </div>
              
              <div class="current-main">
                <div class="temperature">
                  <span class="temp-value">{{ now.now?.temp }}</span>
                  <span class="temp-unit">℃</span>
                </div>
                <div class="weather-info">
                  <div class="weather-desc">
                    <span class="weather-icon">{{ getWeatherIcon(now.now?.icon) }}</span>
                    <span class="weather-text">{{ now.now?.text }}</span>
                  </div>
                  <div class="weather-details">
                    <span>💨 {{ now.now?.windDir }} {{ now.now?.windScale }}级</span>
                    <span>💧 湿度 {{ now.now?.humidity }}%</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 预报容器 -->
            <div class="forecast-container">
              <!-- 24小时预报 -->
              <div class="forecast-section">
                <div class="section-header">
                  <h3 class="section-title">⏰ 未来24小时</h3>
                  <button 
                    v-if="hourly.length > 12" 
                    @click="toggleHourlyExpand"
                    class="expand-btn"
                  >
                    {{ showFullHourly ? '收起' : '展开全部' }}
                    <span class="expand-icon">{{ showFullHourly ? '↑' : '↓' }}</span>
                  </button>
                </div>
                <div v-if="hourly.length === 0" class="empty-message">暂无24小时预报数据</div>
                <div v-else class="hourly-forecast-module">
                  <div 
                    v-for="(hour, index) in displayedHourly" 
                    :key="hour.fxTime" 
                    class="hour-card"
                    :class="{ 'current': index === 0 }"
                  >
                    <div class="hour-time">{{ hour.fxTime.slice(11, 16) }}</div>
                    <div class="hour-icon">{{ getWeatherIcon(hour.icon) }}</div>
                    <div class="hour-temp">{{ hour.temp }}°</div>
                    <div class="hour-desc">{{ hour.text }}</div>
                  </div>
                </div>
              </div>

              <!-- 7天预报 -->
              <div class="forecast-section">
                <h3 class="section-title">📅 未来7天</h3>
                <div v-if="daily.length === 0" class="empty-message">
                  暂无7天预报数据
                  <br>
                  <small>请检查网络连接或重新搜索城市</small>
                </div>
                <div v-else class="daily-grid">
                  <div 
                    v-for="(day, index) in daily" 
                    :key="day.fxDate" 
                    class="daily-card"
                    :class="{ 'today': index === 0 }"
                  >
                    <div class="day-date">
                      {{ index === 0 ? '今天' : new Date(day.fxDate).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }) }}
                    </div>
                    <div class="day-weather">
                      <div class="day-icon">{{ getWeatherIcon(day.iconDay) }}</div>
                      <div class="day-desc">{{ day.textDay }}</div>
                    </div>
                    <div class="day-temp">
                      <span class="temp-high">{{ day.tempMax }}°</span>
                      <span class="temp-low">{{ day.tempMin }}°</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading && !now" class="loading-state">
        <div class="loading-spinner">🌀</div>
        <p>正在获取天气信息...</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* --- 1. App 外层容器：负责背景 --- */
.app {
  min-height: 100vh;
  /* 背景移到body，这里不需要了 */
  padding: 0 !important;
  margin: 0 !important;
}

/* --- 2. 主容器：负责标题 --- */
.container {
  max-width: 2200px; /* 进一步增加容器最大宽度，让右侧更宽 */
  margin: 0 auto !important;
  padding: clamp(1rem, 1.5vw, 2rem) !important; /* 适当增加padding */
  color: #2d3436;
  min-height: 100vh;
}

/* --- 3. 核心布局：使用 CSS Grid 构建主画板 --- */
.weather-app {
  display: grid;
  /* 移动端默认为单列 */
  grid-template-columns: 1fr; 
  /* gap 是行与行或列与列之间的间距 */
  gap: clamp(1.5rem, 3vw, 2rem);
  
  /* 我们把 min-height 移到外层 .container 上，让结构更清晰 */
  /* min-height: calc(100vh - 8rem);  <--  可以删除这一行 */
}

/* --- 4. 侧边栏和主内容区样式 --- */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: clamp(2rem, 4vw, 3rem); /* 增大间距避免重叠 */
  height: fit-content;
  align-items: center; /* 居中对齐 */
  width: 100%;
}

/* 我们把它变成一个透明的、只负责布局的容器 */
.main-content {
  /* display: flex;  <-- 如果有，可以先去掉 */
  /* flex-direction: column; <-- 如果有，可以先去掉 */
  /* gap: 1.5rem; <-- 如果有，可以先去掉 */
  
  /* 清空它的所有视觉样式，因为它不再是“卡片”了 */
  background: none;
  backdrop-filter: none;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  border: none;
  overflow: visible; /* 关键：允许子元素溢出，这样滚动条才能正常工作 */
}

/* 📰 标题区域 */
.header {
  text-align: center;
  margin-bottom: clamp(1.5rem, 4vw, 3rem);
  position: relative;
  z-index: 10; /* 确保标题在最上层 */
}

.title {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.title .icon {
  margin-right: 0.5rem;
}

.subtitle {
  color: rgba(255,255,255,0.9);
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  margin: 0;
}

/* 搜索区域卡片样式 - 独立模块 */
.search-section {
  margin: 0 auto;
  padding: 1.5rem;
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(20px);
  border-radius: 1.25rem;
  box-shadow: 
    0 20px 40px rgba(0,0,0,0.1),
    0 8px 16px rgba(0,0,0,0.06),
    0 1px 4px rgba(0,0,0,0.04);
  border: 1px solid rgba(255,255,255,0.8);
  transition: all 0.3s ease;
  overflow: visible;
  width: 90%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 收藏区域卡片样式 - 独立模块 */
.favorites-section {
  margin: 0 auto;
  padding: 1.5rem;
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(20px);
  border-radius: 1.25rem;
  box-shadow: 
    0 20px 40px rgba(0,0,0,0.1),
    0 8px 16px rgba(0,0,0,0.06),
    0 1px 4px rgba(0,0,0,0.04);
  border: 1px solid rgba(255,255,255,0.8);
  transition: all 0.3s ease;
  overflow: visible;
  width: 90%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 天气显示区域卡片样式 - 独立模块 */
.weather-section {
  margin: 0;
  padding: 2rem;
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(15px);
  border-radius: 1.25rem;
  box-shadow: 
    0 20px 40px rgba(0,0,0,0.1),
    0 8px 16px rgba(0,0,0,0.06),
    0 1px 4px rgba(0,0,0,0.04);
  border: 1px solid rgba(255,255,255,0.6);
  transition: all 0.3s ease;
  overflow: visible;
  width: 100%;
  box-sizing: border-box;
}

.search-section:hover,
.favorites-section:hover,
.weather-section:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 25px 50px rgba(0,0,0,0.15),
    0 12px 20px rgba(0,0,0,0.08),
    0 2px 8px rgba(0,0,0,0.06);
}

/* 🔍 搜索区域样式 */
.search-header {
  margin-bottom: 1rem;
}

.search-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3436;
  margin: 0;
}

.search-bar {
  position: relative;
  margin-bottom: 1.5rem;
}

/* 搜索区域样式 */
.search-section {
  position: relative;
  min-height: fit-content;
  transition: all 0.3s ease;
}

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

/* 搜索输入框样式 - 独立模块 */
.search-input {
  flex: 1;
  margin: 0;
  padding: clamp(1rem, 2.5vw, 1.5rem) clamp(1.5rem, 3vw, 2rem);
  border: 2px solid #e9ecef;
  border-radius: 0.75rem;
  font-size: clamp(0.9rem, 2vw, 1rem);
  transition: all 0.3s ease;
  outline: none;
  background: white;
}

.search-input:focus {
  border-color: #0984e3;
  box-shadow: 0 0 0 3px rgba(9,132,227,0.1);
}

/* 搜索按钮样式 - 独立模块 */
.search-btn {
  margin: 0;
  padding: clamp(1rem, 2.5vw, 1.5rem) clamp(1.25rem, 3vw, 1.75rem);
  background: #0984e3;
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-size: clamp(1rem, 2.5vw, 1.2rem);
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 3rem;
}

.search-btn:hover:not(:disabled) {
  background: #0770c7;
  transform: translateY(-1px);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.options-dropdown {
  position: absolute;
  top: calc(100% + 8px); /* 与搜索框有适当间距 */
  left: 0;
  right: 0;
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(15px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.8);
  overflow: hidden;
  z-index: 2000;
  max-height: 250px; /* 稍微增加高度 */
  overflow-y: auto;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px; /* 增加内边距，避免文字贴边 */
  border-bottom: 1px solid #f1f3f4;
  background: #f8f9fa;
  border-radius: 1rem 1rem 0 0;
  font-weight: 600;
  color: #2d3436;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #636e72;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: rgba(0,0,0,0.1);
  color: #2d3436;
}

.option-item {
  padding: 18px 24px; /* 增加内边距，避免文字贴边 */
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid #f1f3f4;
  font-size: 0.95rem;
  color: #2d3436;
}

.option-item:hover {
  background: #f8f9fa;
}

.option-item:last-child {
  border-bottom: none;
}

/* 收藏按钮样式 - 独立模块 */
.favorite-btn {
  margin: 0;
  padding: 0.75rem 1.5rem;
  background: #00b894;
  color: white;
  border: none;
  border-radius: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.favorite-btn:hover:not(.disabled) {
  background: #00a085;
  transform: translateY(-1px);
}

.favorite-btn.disabled {
  background: #ddd;
  cursor: not-allowed;
}

/* 错误消息 */
.error-message {
  background: rgba(255,255,255,0.95);
  color: #d63031;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  border-left: 4px solid #d63031;
}

/* 收藏城市 */
.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.favorites-count {
  background: rgba(9, 132, 227, 0.1);
  color: #0984e3;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2d3436;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(9, 132, 227, 0.1);
  color: #0984e3;
  border: 1px solid rgba(9, 132, 227, 0.2);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.expand-btn:hover {
  background: rgba(9, 132, 227, 0.2);
  border-color: rgba(9, 132, 227, 0.4);
  transform: translateY(-1px);
}

.expand-icon {
  font-weight: bold;
  transition: transform 0.3s ease;
}

/* 省份分组样式 */
.province-group {
  margin-bottom: 1.5rem;
}

.province-group:last-child {
  margin-bottom: 0;
}

/* 省份标题样式 - 独立模块 */
.province-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem 0;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(0,0,0,0.1);
  background: rgba(248,249,250,0.5);
  border-radius: 0.5rem;
}

.province-name {
  font-weight: 600;
  color: #2d3436;
  font-size: 0.95rem;
}

.province-count {
  color: #636e72;
  font-size: 0.85rem;
}

.province-cities {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); /* 增加最小宽度 */
  gap: 1rem; /* 增加间距 */
}

/* 收藏城市卡片样式 - 独立模块 */
.favorite-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0.5rem 0;
  padding: 1rem 1.25rem;
  background: rgba(248,249,250,0.8);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid rgba(255,255,255,0.6);
}

.favorite-card:hover {
  background: rgba(255,255,255,0.95);
  border-color: #0984e3;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(9,132,227,0.2);
}

/* 城市名称样式 - 独立模块 */
.city-name {
  margin: 0;
  padding: 0.25rem 0.5rem;
  font-weight: 500;
  color: #2d3436;
  font-size: 0.9rem;
}

/* 移除按钮样式 - 独立模块 */
.remove-btn {
  margin: 0;
  padding: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.remove-btn:hover {
  opacity: 1;
}

/* 天气信息 */
.weather-section {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.current-weather {
  margin-bottom: 32px;
}

.current-header {
  display: flex;
  justify-content: center; /* 居中对齐 */
  align-items: center;
  margin-bottom: clamp(1.5rem, 3vw, 2.5rem);
  text-align: center;
  flex-direction: column;
  gap: 0.75rem;
}

.current-header .city-name {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.update-time {
  font-size: 0.9rem;
  color: #636e72;
}

.current-main {
  display: flex;
  align-items: center;
  justify-content: center; /* 居中对齐 */
  gap: clamp(2rem, 4vw, 4rem); /* 响应式间距 */
  text-align: center;
}

.temperature {
  display: flex;
  align-items: baseline;
}

/* 🌡️ 流体温度显示 - 核心特性！ */
.temp-value {
  font-size: clamp(3.5rem, 10vw, 8rem); /* 增大温度字体 */
  font-weight: 300;
  color: #0984e3;
}

.temp-unit {
  font-size: 1.5rem;
  color: #636e72;
  margin-left: 4px;
}

.weather-info {
  flex: 1;
}

.weather-desc {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.weather-icon {
  font-size: 2rem;
}

.weather-text {
  font-size: 1.3rem;
  font-weight: 500;
}

.weather-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  color: #636e72;
}

/* 预报部分 */
.forecast-section {
  margin-bottom: 32px;
}

.forecast-section:last-child {
  margin-bottom: 0;
}

/* --- 5. 【重点】处理24小时天气模块 - 改为多行网格布局 --- */
.hourly-forecast-module {
  display: grid;
  grid-template-columns: repeat(6, 1fr); /* 6个卡片一行 */
  gap: clamp(1rem, 2vw, 1.5rem); /* 增大间距 */
  padding: clamp(1.5rem, 3vw, 2rem) 0;
  justify-items: center; /* 卡片居中 */
  /* 移动端滚动体验优化 */
  -webkit-overflow-scrolling: touch;
}

.hourly-forecast-module::-webkit-scrollbar {
  height: 6px;
}

.hourly-forecast-module::-webkit-scrollbar-thumb {
  background: rgba(226, 232, 240, 0.8);
  border-radius: 3px;
}

.hourly-forecast-module::-webkit-scrollbar-track {
  background: transparent;
}

/* 🖱️ 拖拽体验优化 */
.hourly-forecast-module {
  cursor: grab;
  user-select: none;
}

.hourly-forecast-module.dragging {
  cursor: grabbing;
}

.hourly-forecast-module.dragging .hour-card {
  pointer-events: none;
  transform: none !important;
}

.hourly-forecast-module:not(.dragging) .hour-card {
  pointer-events: auto;
}

/* 24小时天气卡片样式 - 独立模块 */
.hour-card {
  flex-shrink: 0;
  width: clamp(90px, 14vw, 120px);
  margin: 0.25rem;
  padding: 1.25rem 1rem;
  background: rgba(248, 249, 250, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid rgba(255,255,255,0.5);
}

.hour-card.current {
  background: linear-gradient(135deg, #0984e3, #74b9ff);
  color: white;
  box-shadow: 0 8px 20px rgba(9,132,227,0.3);
}

.hour-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  background: rgba(255,255,255,0.95);
}

.hour-time {
  font-size: 0.9rem;
  margin-bottom: 8px;
  font-weight: 500;
}

.hour-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.hour-temp {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 4px;
}

.hour-desc {
  font-size: 0.8rem;
  opacity: 0.8;
}

.daily-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr); /* 7天一行 */
  gap: clamp(1rem, 2vw, 1.5rem); /* 增大间距 */
  justify-items: center; /* 卡片居中 */
}

/* 7天天气卡片样式 - 独立模块 */
.daily-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.75rem;
  margin: 0.25rem;
  padding: 1.25rem 1rem;
  background: rgba(248,249,250,0.8);
  backdrop-filter: blur(10px);
  border-radius: 1rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(255,255,255,0.6);
}

.daily-card.today {
  background: rgba(232,245,255,0.9);
  border: 2px solid #0984e3;
  box-shadow: 0 4px 15px rgba(9,132,227,0.15);
}

.daily-card:hover {
  background: rgba(255,255,255,0.95);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.1);
}

.day-date {
  font-weight: 600;
  font-size: 0.9rem;
}

.day-weather {
  display: flex;
  align-items: center;
  gap: 12px;
}

.day-icon {
  font-size: 1.5rem;
}

.day-desc {
  font-size: 0.95rem;
}

.day-temp {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.temp-high {
  font-weight: 600;
  font-size: 1rem;
}

.temp-low {
  color: #636e72;
  font-size: 0.9rem;
}

/* 右侧面板样式 */
.weather-stats {
  background: rgba(255,255,255,0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.stats-grid {
  display: grid;
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
}

.stat-label {
  font-size: 0.9rem;
  color: #636e72;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2d3436;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 60px 20px;
  color: white;
}

.loading-spinner {
  font-size: 3rem;
  margin-bottom: 16px;
  animation: spin 2s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 下拉框动画效果 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.3s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.98);
}

/* 收藏框被推下时的样式 */
.favorites-section.pushed-down {
  margin-top: 280px; /* 为下拉框预留空间 */
  transition: margin-top 0.3s ease;
}

/* 收藏框动画效果 */
.favorites-enter-active,
.favorites-leave-active {
  transition: all 0.3s ease;
}

.favorites-enter-from,
.favorites-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}



/* --- 6. 桌面端布局：Grid 的威力 --- */
@media (min-width: 768px) {
  .weather-app {
    /* 桌面端：两列布局 - 侧边栏400px，主内容充分利用剩余空间 */
    grid-template-columns: 400px 1fr;
    grid-template-rows: 1fr;
    gap: clamp(1.5rem, 2vw, 2.5rem);
    max-width: 2000px; /* 进一步增加最大宽度让右侧更宽 */
    margin: 0 auto; /* 居中整个布局 */
    width: 98%; /* 接近全宽，充分利用空间 */
  }
  
  /* 桌面端预报区域垂直排列，不并排 */
  .forecast-container {
    display: flex;
    flex-direction: column;
    gap: 2rem; /* 增大间距 */
  }
  
  /* 桌面端侧边栏卡片宽度调整 */
  .sidebar .search-section,
  .sidebar .favorites-section {
    width: 95%; /* 桌面端减少宽度避免贴边 */
  }
}

/* 🎯 移动端特殊优化 */
@media (max-width: 767px) {
  .input-wrapper {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-btn {
    width: 100%;
    justify-content: center;
  }
  
  .current-main {
    flex-direction: column;
    text-align: center;
    gap: 1.5rem;
  }
  
  .current-header {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }

  .hourly-forecast-module {
    grid-template-columns: repeat(4, 1fr); /* 移动端4个一行 */
    gap: 0.5rem;
    padding: 1rem 0;
  }

  .hour-card {
    min-width: auto; /* 移除固定宽度限制 */
  }

  .daily-grid {
    grid-template-columns: repeat(3, 1fr); /* 移动端3个一行，分两行显示7天 */
    gap: 0.5rem;
  }

  .daily-card {
    padding: 0.75rem 0.25rem; /* 移动端减小padding */
  }
}

.empty-message {
  text-align: center;
  color: #636e72;
  padding: 1rem;
  font-style: italic;
}
</style>

<!-- 全局样式重置 -->
<style>
/* --- 全局重置与设定 --- */
* {
  box-sizing: border-box;
}

/* 只重置真正需要重置的元素 */
html, body {
  margin: 0;
  padding: 0;
}

/* 布局容器重置 */
#app, .container, .weather-app {
  margin: 0;
  padding: 0;
}

html {
  height: 100%;
  font-size: clamp(14px, 2vw, 16px);
  margin: 0 !important;
  padding: 0 !important;
}

body {
  margin: 0 !important;
  padding: 0 !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 50%, #6c5ce7 100%);
  background-attachment: fixed;
  background-size: cover;
  background-repeat: no-repeat;
  min-height: 100vh;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  margin: 0 !important;
  padding: 0 !important;
  background: inherit;
}
</style>
