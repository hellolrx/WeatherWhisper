<script setup lang="ts">
import { ref, defineEmits, defineProps, onMounted, computed } from 'vue'
import type { CityOption } from '../../types/weather'

// Props
interface Props {
  loading?: boolean
  options?: CityOption[]
  showOptions?: boolean
  errorMsg?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  options: () => [],
  showOptions: false,
  errorMsg: ''
})

// Events
const emit = defineEmits<{
  search: [query: string]
  selectCity: [city: CityOption]
  input: [query: string]
  closeOptions: []
  toggleSuggestions: [open: boolean]
}>()

// Local state
const query = ref('')
const searchTimeout = ref<number | null>(null)
const showSuggestions = ref(false)
const searchHistory = ref<string[]>([])
const cities = ref<Array<{id: string, name: string, adm1: string, adm2: string, level: string, type: string}>>([])
const districts = ref<Array<{id: string, name: string, adm1: string, adm2: string, level: string, type: string}>>([])

// 计算属性
const hasQuery = computed(() => query.value.trim().length > 0)
const hasHistory = computed(() => searchHistory.value.length > 0)
const filteredHistory = computed(() => {
  if (!hasQuery.value) return searchHistory.value
  return searchHistory.value.filter(item => 
    item.toLowerCase().includes(query.value.toLowerCase())
  )
})

// 从localStorage加载搜索历史
function loadSearchHistory() {
  try {
    const history = localStorage.getItem('ww_search_history')
    if (history) {
      searchHistory.value = JSON.parse(history)
    }
  } catch {
    searchHistory.value = []
  }
}

// 保存搜索历史到localStorage
function saveSearchHistory(query: string) {
  try {
    const history = new Set(searchHistory.value)
    history.delete(query)
    searchHistory.value = [query, ...Array.from(history).slice(0, 19)]
    localStorage.setItem('ww_search_history', JSON.stringify(searchHistory.value))
  } catch {}
}

// 清除搜索历史
function clearSearchHistory() {
  searchHistory.value = []
  localStorage.removeItem('ww_search_history')
}

// 简化的搜索逻辑 - 完全依赖和风天气API，但智能分组显示
async function performSearch(searchQuery: string) {
  try {
    // 直接使用和风天气的原生城市搜索API
    const response = await fetch(`http://127.0.0.1:8000/api/geo?query=${encodeURIComponent(searchQuery)}`)
    const data = await response.json()
    
    if (data.code === '200' && data.location && data.location.length > 0) {
      // 显示搜索结果
      showSuggestions.value = true
      
      // 智能分析搜索结果并分组
      const { cities: cityResults, districts: districtResults } = analyzeSearchResults(data.location)
      
      // 根据搜索类型决定显示策略
      if (searchQuery.includes('省') && cityResults.length > 0 && districtResults.length > 0) {
        // 搜索省份时，如果既有城市又有区县，分组显示
        cities.value = cityResults
        districts.value = districtResults
      } else {
        // 其他情况，直接显示所有结果
        cities.value = data.location.sort((a: any, b: any) => {
          const rankA = parseInt(a.rank || '999')
          const rankB = parseInt(b.rank || '999')
          return rankA - rankB
        })
        districts.value = []
      }
      
      return
    }
    
  } catch (error) {
    console.error('搜索失败:', error)
  }
}

// 智能分析搜索结果，区分城市和区县
function analyzeSearchResults(locations: any[]) {
  const cities: any[] = []
  const districts: any[] = []
  
  for (const location of locations) {
    const name = location.name || ''
    const adm2 = location.adm2 || ''
    
    if (adm2 && adm2 !== name) {
      // 区县级别：adm2 和 name 不同
      // 例如：增城 (name: "增城", adm2: "广州")
      districts.push(location)
    } else {
      // 城市级别：adm2 和 name 相同或为空
      // 例如：广州 (name: "广州", adm2: "广州")
      cities.push(location)
    }
  }
  
  // 按rank排序
  cities.sort((a, b) => parseInt(a.rank || '999') - parseInt(b.rank || '999'))
  districts.sort((a, b) => parseInt(a.rank || '999') - parseInt(b.rank || '999'))
  
  return { cities, districts }
}

// 选择城市
async function selectCity(city: any) {
  const fullName = `${city.adm1 || ''} ${city.name || ''}`.trim()
  
  const cityOption: CityOption = {
    id: city.id || '',
    name: city.name || '',
    adm1: city.adm1 || '',
    adm2: city.adm2 || '',
    fullName: fullName
  }

  // 更新搜索框内容
  query.value = fullName

  emit('selectCity', cityOption)
  saveSearchHistory(fullName)
  showSuggestions.value = false
  emit('toggleSuggestions', false)
}

// 搜索输入处理
function handleSearchInput() {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = window.setTimeout(() => {
    if (query.value.trim()) {
      performSearch(query.value.trim())
      // 输入时确保建议可见
      if (!showSuggestions.value) {
        showSuggestions.value = true
        emit('toggleSuggestions', true)
      }
    } else {
      showSuggestions.value = false
      emit('toggleSuggestions', false)
      cities.value = []
      districts.value = []
    }
  }, 300)
}

// 处理搜索
function handleSearch() {
  if (query.value.trim()) {
    performSearch(query.value.trim())
    if (!showSuggestions.value) {
      showSuggestions.value = true
      emit('toggleSuggestions', true)
    }
  }
}

// 处理回车键
function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    handleSearch()
  }
}

// 关闭建议
function closeSuggestions() {
  showSuggestions.value = false
  emit('toggleSuggestions', false)
}

// 组件挂载时加载搜索历史
onMounted(() => {
  loadSearchHistory()
})
</script>

<template>
  <div class="search-section">
    <div class="search-header">
      <h3 class="search-title">🔍 搜索城市</h3>
    </div>
    
    <div class="search-bar">
      <div class="input-wrapper">
        <input 
          v-model="query" 
          placeholder="输入省份、城市或区县，例如：北京、广东广州、浙江杭州西湖区" 
          @input="handleSearchInput"
          @keyup="handleKeydown"
          @focus="showSuggestions = true; emit('toggleSuggestions', true)"
          @blur="closeSuggestions"            
          class="search-input"
        />
        <button 
          @click="handleSearch" 
          :disabled="loading" 
          class="search-btn"
        >
          <span v-if="loading">🔄</span>
          <span v-else>🔍</span>
        </button>
      </div>
    </div>

    <!-- 搜索建议 -->
    <Transition name="suggestions">
      <div v-if="showSuggestions && !props.showOptions" class="search-suggestions">
        <!-- 城市选择 -->
        <div v-if="cities.length > 0" class="suggestion-section">
          <div class="suggestion-header">
            <span class="suggestion-title">🏙️ 城市级别</span>
            <span class="suggestion-subtitle">选择要查询的城市</span>
          </div>
          <div class="suggestion-list">
            <div 
              v-for="city in cities" 
              :key="city.id"
              @click="selectCity(city)"
              class="suggestion-item city-item"
            >
              <span class="suggestion-icon">🏙️</span>
              <span class="suggestion-text">{{ city.name }}</span>
              <span class="city-info">{{ city.adm1 }} · {{ city.adm2 }}</span>
            </div>
          </div>
        </div>

        <!-- 区县选择 -->
        <div v-if="districts.length > 0" class="suggestion-section">
          <div class="suggestion-header">
            <span class="suggestion-title">📍 区县级别</span>
            <span class="suggestion-subtitle">选择要查询的区县</span>
          </div>
          <div class="suggestion-list">
            <div 
              v-for="district in districts" 
              :key="district.id"
              @click="selectCity(district)"
              class="suggestion-item district-item"
            >
              <span class="suggestion-icon">📍</span>
              <span class="suggestion-text">{{ district.name }}</span>
              <span class="city-info">{{ district.adm1 }} · {{ district.adm2 }}</span>
            </div>
          </div>
        </div>

        <!-- 搜索历史 -->
        <div v-if="hasHistory && filteredHistory.length > 0" class="suggestion-section">
          <div class="suggestion-header">
            <span class="suggestion-title">📚 搜索历史</span>
            <button @click="clearSearchHistory" class="clear-history-btn" title="清除历史">
              🗑️
            </button>
          </div>
          <div class="suggestion-list">
            <div 
              v-for="historyItem in filteredHistory" 
              :key="historyItem"
              @click="query = historyItem; handleSearch()"
              class="suggestion-item history-item"
            >
              <span class="suggestion-icon">🕒</span>
              <span class="suggestion-text">{{ historyItem }}</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-message">
      {{ errorMsg }}
    </div>
  </div>
</template>

<style scoped>
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

.search-section:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 25px 50px rgba(0,0,0,0.15),
    0 12px 20px rgba(0,0,0,0.08),
    0 2px 8px rgba(0,0,0,0.06);
}

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

.input-wrapper {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

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
  text-align: center;
}

.search-input:focus {
  border-color: #0984e3;
  box-shadow: 0 0 0 3px rgba(9,132,227,0.1);
}

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
  display: flex;
  align-items: center;
  justify-content: center;
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
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(15px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.8);
  overflow: hidden;
  z-index: 2000;
  max-height: 250px;
  overflow-y: auto;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
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
  padding: 18px 24px;
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

.error-message {
  background: rgba(255,255,255,0.95);
  color: #d63031;
  padding: 16px 20px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  border-left: 4px solid #d63031;
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

/* 搜索建议样式 */
.search-suggestions {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: rgba(255,255,255,0.98);
  backdrop-filter: blur(15px);
  border-radius: 1rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.15);
  border: 1px solid rgba(255,255,255,0.8);
  z-index: 2000;
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  box-sizing: border-box;
}

.suggestion-section {
  border-bottom: 1px solid #f1f3f4;
  padding-bottom: 1rem;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f3f4;
  font-weight: 600;
  color: #2d3436;
}

.clear-history-btn {
  background: none;
  border: none;
  font-size: 1rem;
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

.clear-history-btn:hover {
  background: rgba(0,0,0,0.1);
  color: #2d3436;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.95rem;
  color: #2d3436;
}

.suggestion-item:hover {
  background: #f8f9fa;
  transform: translateX(5px);
}

.suggestion-icon {
  font-size: 1.1rem;
}

.suggestion-text {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-subtext {
  font-size: 0.8rem;
  color: #636e72;
  margin-top: 0.25rem;
}

.history-item .suggestion-subtext {
  display: none; /* 隐藏历史记录的子文本 */
}

.popular-item .suggestion-subtext {
  display: block; /* 显示热门城市的子文本 */
}

/* 层级选择项目样式 */
.province-item {
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
  color: white;
  border: 1px solid #0984e3;
}

.province-item:hover {
  background: linear-gradient(135deg, #0984e3 0%, #0770c7 100%);
  transform: translateX(5px) scale(1.02);
}

.city-item {
  background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
  color: white;
  border: 1px solid #e84393;
}

.city-item:hover {
  background: linear-gradient(135deg, #e84393 0%, #c44569 100%);
  transform: translateX(5px) scale(1.02);
}

.district-item {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
  border: 1px solid #00a085;
}

.district-item:hover {
  background: linear-gradient(135deg, #00a085 0%, #008f7a 100%);
  transform: translateX(5px) scale(1.02);
}

/* 建议子标题样式 */
.suggestion-subtitle {
  font-size: 0.875rem;
  color: #666;
  margin-left: 0.5rem;
}

/* 搜索建议动画 */
.suggestions-enter-active,
.suggestions-leave-active {
  transition: all 0.3s ease;
}

.suggestions-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.suggestions-leave-to {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

/* 移动端响应式 */
@media (max-width: 767px) {
  .input-wrapper {
    flex-direction: column;
    gap: 1rem;
  }
  
  .search-btn {
    width: 100%;
    justify-content: center;
  }
}

/* 层级选择提示样式 */
.selection-path {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-radius: 0.75rem;
  border: 1px solid #e9ecef;
  font-size: 0.9rem;
  color: #2d3436;
}

.path-label {
  font-weight: 500;
}

.path-item {
  cursor: pointer;
  color: #0984e3;
  text-decoration: underline;
}

.path-item:hover {
  color: #0770c7;
}

.reset-btn {
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

.reset-btn:hover {
  background: rgba(0,0,0,0.1);
  color: #2d3436;
}

/* 热门城市快速选择样式 */
.province-group {
  margin-bottom: 1rem;
}

.province-header {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3436;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f1f3f4;
}

.cities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 0.75rem;
}

.city-chip {
  background: #e9ecef;
  color: #2d3436;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  text-align: center;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid #dcdde1;
}

.city-chip:hover {
  background: #dee2e6;
  border-color: #ced4da;
}

/* 返回按钮 */
.back-btn {
  background: #f0f0f0;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #e0e0e0;
  color: #333;
}

/* 加载状态 */
.loading-spinner {
  text-align: center;
  padding: 2rem;
  font-size: 2rem;
  color: #666;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 城市信息 */
.city-info {
  font-size: 0.75rem;
  color: #666;
  margin-left: 0.5rem;
}

</style>
