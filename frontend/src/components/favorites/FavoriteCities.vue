<script setup lang="ts">
import { computed, defineEmits, defineProps } from 'vue'
import type { FavoriteCity, CityOption } from '../../types/weather'

// Props
interface Props {
  favorites: FavoriteCity[]
  limit: number
  selectedCity?: CityOption | null
  showOptions?: boolean
  optionsLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  favorites: () => [],
  limit: 10,
  selectedCity: null,
  showOptions: false,
  optionsLength: 0
})

// Events
const emit = defineEmits<{
  loadWeather: [city: FavoriteCity]
  removeFavorite: [id: string]
  addFavorite: [city: CityOption]
}>()

// Computed
const favoritesByProvince = computed(() => {
  const grouped: Record<string, FavoriteCity[]> = {}
  props.favorites.forEach(city => {
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
         !props.favorites.find(c => c.id === props.selectedCity?.id) &&
         props.favorites.length < props.limit
})

// Methods
function handleAddFavorite() {
  if (props.selectedCity && canAddFavorite.value) {
    emit('addFavorite', props.selectedCity)
  }
}
</script>

<template>
  <div class="favorites-wrapper">
    <!-- 收藏按钮 -->
    <button 
      v-if="selectedCity" 
      @click="handleAddFavorite" 
      :disabled="!canAddFavorite"
      class="favorite-btn"
      :class="{ 'disabled': !canAddFavorite }"
    >
      {{ canAddFavorite ? '⭐ 收藏' : '✅ 已收藏' }}
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
          <span class="favorites-count">{{ favorites.length }}/{{ limit }}</span>
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
                @click="emit('loadWeather', city)"
              >
                <span class="city-name">{{ city.name }}</span>
                <button 
                  @click.stop="emit('removeFavorite', city.id)"
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
  width: 90%;
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
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
}

/* 收藏城市卡片样式 */
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

.city-name {
  margin: 0;
  padding: 0.25rem 0.5rem;
  font-weight: 500;
  color: #2d3436;
  font-size: clamp(0.95rem, 2.2vw, 1.1rem);
  transition: color 0.2s ease;
}

.favorite-card:hover .city-name {
  color: #0984e3;
}

.remove-btn {
  margin: 0;
  padding: 0.25rem;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.8rem;
  opacity: 0;
  transition: opacity 0.3s ease;
  flex-shrink: 0;
}

.favorite-card:hover .remove-btn {
  opacity: 0.7;
}

.remove-btn:hover {
  opacity: 1;
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

/* 移动端响应式调整 */
@media (min-width: 768px) {
  .favorites-section {
    width: 95%;
  }
}
</style>
