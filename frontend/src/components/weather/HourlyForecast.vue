<script setup lang="ts">
import { ref, computed, nextTick, onMounted, defineProps } from 'vue'
import type { HourlyWeather } from '../../types/weather'
import { getWeatherIcon } from '../../utils/weather/icons'

// Props
interface Props {
  hourlyData: HourlyWeather[]
}

const props = defineProps<Props>()

// State
const showFullHourly = ref(false)

// Computed
const displayedHourly = computed(() => {
  if (showFullHourly.value) {
    return props.hourlyData // 显示全部24小时
  } else {
    return props.hourlyData.slice(0, 12) // 只显示前12小时
  }
})

// Methods
function toggleHourlyExpand() {
  showFullHourly.value = !showFullHourly.value
}

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

// 初始化拖拽功能
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

onMounted(() => {
  initializeDragScrolling()
})
</script>

<template>
  <div class="forecast-section">
    <div class="section-header">
      <h3 class="section-title">⏰ 未来24小时</h3>
      <button 
        v-if="hourlyData.length > 12" 
        @click="toggleHourlyExpand"
        class="expand-btn"
      >
        {{ showFullHourly ? '收起' : '展开全部' }}
        <span class="expand-icon">{{ showFullHourly ? '↑' : '↓' }}</span>
      </button>
    </div>
    
    <div v-if="hourlyData.length === 0" class="empty-message">
      暂无24小时预报数据
    </div>
    
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
</template>

<style scoped>
.forecast-section {
  margin-bottom: 32px;
}

.forecast-section:last-child {
  margin-bottom: 0;
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

.empty-message {
  text-align: center;
  color: #636e72;
  padding: 1rem;
  font-style: italic;
}

/* 24小时天气模块 */
.hourly-forecast-module {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: clamp(1rem, 2vw, 1.5rem);
  padding: clamp(1.5rem, 3vw, 2rem) 0;
  justify-items: center;
  -webkit-overflow-scrolling: touch;
  cursor: grab;
  user-select: none;
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

/* 24小时天气卡片样式 */
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

/* 移动端响应式 */
@media (max-width: 767px) {
  .hourly-forecast-module {
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
    padding: 1rem 0;
  }

  .hour-card {
    min-width: auto;
  }
}
</style>
