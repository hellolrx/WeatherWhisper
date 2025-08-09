<script setup lang="ts">
import { defineProps } from 'vue'
import type { DailyWeather } from '../../types/weather'
import { getWeatherIcon } from '../../utils/weather/icons'

// Props
interface Props {
  dailyData: DailyWeather[]
}

defineProps<Props>()
</script>

<template>
  <div class="forecast-section">
    <h3 class="section-title">📅 未来7天</h3>
    
    <div v-if="dailyData.length === 0" class="empty-message">
      暂无7天预报数据
      <br>
      <small>请检查网络连接或重新搜索城市</small>
    </div>
    
    <div v-else class="daily-grid">
      <div 
        v-for="(day, index) in dailyData" 
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
</template>

<style scoped>
.forecast-section {
  margin-bottom: 32px;
}

.forecast-section:last-child {
  margin-bottom: 0;
}

.section-title {
  margin: 0;
  font-size: 1.3rem;
  font-weight: 600;
  color: #2d3436;
  margin-bottom: 16px;
}

.empty-message {
  text-align: center;
  color: #636e72;
  padding: 1rem;
  font-style: italic;
}

.daily-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: clamp(1rem, 2vw, 1.5rem);
  justify-items: center;
}

/* 7天天气卡片样式 */
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

/* 移动端响应式 */
@media (max-width: 767px) {
  .daily-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }

  .daily-card {
    padding: 0.75rem 0.25rem;
  }
}
</style>
