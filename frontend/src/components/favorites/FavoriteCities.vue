<script setup lang="ts">
import { computed, defineEmits, defineProps, onMounted, watch } from 'vue'
import { useFavoritesStore } from '../../stores/favorites'
import type { FavoriteCity, CityOption } from '../../types/weather'

// Props
interface Props {
  limit: number
  selectedCity?: CityOption | null
  showOptions?: boolean
  optionsLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  limit: 10,
  selectedCity: null,
  showOptions: false,
  optionsLength: 0
})

// Events
const emit = defineEmits<{
  loadWeather: [city: FavoriteCity]
  'open-send-email': [cityId: string]
}>()

// Store
const favoritesStore = useFavoritesStore()

// 监听认证状态变化
watch(() => favoritesStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    favoritesStore.loadFavorites()
  } else {
    favoritesStore.list = []
  }
})

// 组件挂载时初始化
onMounted(() => {
  favoritesStore.init()
})

// Computed
const favorites = computed(() => favoritesStore.list)

const favoritesByProvince = computed(() => {
  const grouped: Record<string, FavoriteCity[]> = {}
  favorites.value.forEach(city => {
    const province = city.adm1 || '其他'
    if (!grouped[province]) {
      grouped[province] = []
    }
    grouped[province].push(city)
  })
  return grouped
})

const canAddFavorite = computed(() => {
  return props.selectedCity && 
         favoritesStore.canAddFavorite(props.selectedCity.id) &&
         !favoritesStore.loading
})

// Methods
async function handleAddFavorite() {
  if (props.selectedCity && canAddFavorite.value) {
    const success = await favoritesStore.add({
      id: props.selectedCity.id,
      name: props.selectedCity.name,
      adm1: props.selectedCity.adm1,
      adm2: props.selectedCity.adm2
    })
    
    if (success) {
      console.log('收藏添加成功')
    }
  }
}

async function handleRemoveFavorite(id: string) {
  const success = await favoritesStore.remove(id)
  if (success) {
    console.log('收藏移除成功')
  }
}

function handleLoadWeather(city: FavoriteCity) {
  emit('loadWeather', city)
}

function handleOpenSend(cityId: string) {
  emit('open-send-email', cityId)
}
</script>

<template>
  <div class="favorites-wrapper">
    <!-- 错误提示 -->
    <div v-if="favoritesStore.error" class="error-message">
      {{ favoritesStore.error }}
      <button @click="favoritesStore.clearError" class="error-close">×</button>
    </div>

    <!-- 收藏按钮 -->
    <button 
      v-if="selectedCity" 
      @click="handleAddFavorite" 
      :disabled="!canAddFavorite"
      class="favorite-btn"
      :class="{ 'disabled': !canAddFavorite, 'loading': favoritesStore.loading }"
    >
      <span v-if="favoritesStore.loading">🔄</span>
      <span v-else-if="canAddFavorite">⭐ 收藏</span>
      <span v-else>✅ 已收藏</span>
    </button>

    <!-- 收藏城市列表 -->
    <Transition name="favorites">
      <div 
        v-if="favorites.length" 
        class="favorites-section" 
        :class="{ 'pushed-down': showOptions && optionsLength > 1 }"
      >
        <div class="favorites-header">
          <h3 class="section-title">📌 已关注的城市</h3>
          <div class="header-actions">
            <span class="favorites-count">{{ favorites.length }}/{{ limit }}</span>
          </div>
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
              >
                <span class="city-name" @click="handleLoadWeather(city)">{{ city.name }}</span>
                <div class="card-actions">
                  <button 
                    @click="handleOpenSend(city.id)"
                    class="send-btn-small"
                    title="发送到邮箱"
                  >
                    ✉️
                  </button>
                  <button 
                    @click.stop="handleRemoveFavorite(city.id)"
                    class="remove-btn"
                    :disabled="favoritesStore.loading"
                    title="移除收藏"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 空状态和加载状态 -->
    <div v-if="!favoritesStore.loading && favorites.length === 0" class="empty-state">
      <p class="empty-text">暂无收藏城市</p>
      <p class="empty-hint">搜索并收藏你喜欢的城市吧！</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="favoritesStore.loading" class="loading-state">
      <p class="loading-text">🔄 加载中...</p>
    </div>
  </div>
</template>

<style scoped>
.favorites-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 收藏按钮样式 */
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

.favorite-btn.loading {
  background: #6c757d;
  cursor: not-allowed;
  transform: none;
}

/* 收藏区域卡片样式 */
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
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.favorites-section:hover {
  transform: translateY(-2px);
  box-shadow: 
    0 25px 50px rgba(0,0,0,0.15),
    0 12px 20px rgba(0,0,0,0.08),
    0 2px 8px rgba(0,0,0,0.06);
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2d3436;
}

.favorites-count {
  background: rgba(9, 132, 227, 0.1);
  color: #0984e3;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: 600;
}

/* 省份分组样式 */
.province-group {
  margin-bottom: 1.5rem;
}

.province-group:last-child {
  margin-bottom: 0;
}

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
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

/* 收藏城市卡片样式 */
.favorite-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 0.5rem 0;
  padding: 0.9rem 1rem;
  background: rgba(248,249,250,0.8);
  backdrop-filter: blur(10px);
  border-radius: 0.75rem;
  transition: all 0.3s ease;
  border: 1px solid rgba(255,255,255,0.6);
  width: 100%;
}

.favorite-card:hover {
  background: rgba(255,255,255,0.95);
  border-color: #0984e3;
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(9,132,227,0.2);
}

.city-name {
  margin: 0;
  padding: 0.15rem 0.25rem;
  font-weight: 500;
  color: #2d3436;
  font-size: clamp(0.95rem, 2.2vw, 1.05rem);
  transition: color 0.2s ease;
  cursor: pointer;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.favorite-card:hover .city-name {
  color: #0984e3;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.send-btn-small {
  margin: 0;
  padding: 0.25rem 0.5rem;
  background: #0984e3;
  color: white;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
  opacity: 0.8;
}

.send-btn-small:hover {
  opacity: 1;
  transform: scale(1.1);
}

.remove-btn {
  margin: 0;
  padding: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  opacity: 0.6;
  transition: opacity 0.3s ease;
  flex-shrink: 0;
}

.remove-btn:hover {
  opacity: 1;
}

.remove-btn:disabled {
  cursor: not-allowed;
  opacity: 0.3;
}

/* 收藏框被推下时的样式 */
.favorites-section.pushed-down {
  margin-top: 280px;
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

/* 错误提示样式 */
.error-message {
  background-color: #f44336;
  color: white;
  padding: 1rem;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.error-message .error-close {
  background: none;
  border: none;
  color: white;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.25rem;
  line-height: 1;
}

/* 空状态样式 */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #636e72;
  font-size: 1.1rem;
}

.empty-text {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.empty-hint {
  font-size: 0.9rem;
}

/* 加载状态样式 */
.loading-state {
  text-align: center;
  padding: 2rem;
  color: #636e72;
  font-size: 1.1rem;
}

.loading-text {
  font-weight: 600;
}

/* 移动端响应式调整 */
@media (min-width: 768px) {
  .favorites-section {
    width: 95%;
  }
}

.header-actions { 
  display: flex; 
  align-items: center; 
  gap: 8px; 
}
</style>
