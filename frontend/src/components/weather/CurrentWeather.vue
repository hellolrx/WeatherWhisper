<script setup lang="ts">
import { defineProps } from 'vue'
import type { CurrentWeather, CityOption } from '../../types/weather'
import { getWeatherIcon } from '../../utils/weather/icons'

// Props
interface Props {
  weather: CurrentWeather
  selectedCity: CityOption
}

defineProps<Props>()
</script>

<template>
  <div class="current-weather">
    <div class="current-header">
      <h2 class="city-name">📍 {{ selectedCity.name }}</h2>
      <div class="update-time">
        更新时间：{{ new Date(weather.updateTime).toLocaleString() }}
      </div>
    </div>
    
    <div class="current-main">
      <div class="temperature">
        <span class="temp-value">{{ weather.now?.temp }}</span>
        <span class="temp-unit">℃</span>
      </div>
      <div class="weather-info">
        <div class="weather-desc">
          <span class="weather-icon main-weather-icon">{{ getWeatherIcon(weather.now?.icon) }}</span>
          <span class="weather-text">{{ weather.now?.text }}</span>
        </div>
        <div class="weather-details">
          <span class="weather-detail-item">
            <span class="weather-icon wind-icon">💨</span>
            {{ weather.now?.windDir }} {{ weather.now?.windScale }}级
          </span>
          <span class="weather-detail-item">
            <span class="weather-icon humidity-icon">💧</span>
            湿度 {{ weather.now?.humidity }}%
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.current-weather {
  margin-bottom: 32px;
}

.current-header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: clamp(1.5rem, 3vw, 2.5rem);
  text-align: center;
  flex-direction: column;
  gap: 0.75rem;
}

/* 当前天气城市名样式 */
.city-name {
  margin: 0;
  font-size: clamp(1.8rem, 4vw, 2.4rem);
  font-weight: 700;
  color: #1a1a1a;
  text-shadow: 0 2px 4px rgba(0,0,0,0.15);
  letter-spacing: 0.8px;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
}

.update-time {
  font-size: 0.9rem;
  color: #636e72;
}

.current-main {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(2rem, 4vw, 4rem);
  text-align: center;
}

.temperature {
  display: flex;
  align-items: baseline;
}

.temp-value {
  font-size: clamp(3.5rem, 10vw, 8rem);
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
  transition: all 0.3s ease;
}

.weather-text {
  font-size: 1.3rem;
  font-weight: 500;
}

/* 天气详情样式 */
.weather-details {
  display: flex;
  flex-direction: column;
  gap: clamp(1rem, 2vw, 1.5rem);
  color: #636e72;
  font-size: clamp(1.1rem, 2.5vw, 1.4rem);
  font-weight: 500;
  margin-top: clamp(1rem, 2vw, 1.5rem);
}

/* 天气详情项样式 */
.weather-detail-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  transition: all 0.3s ease;
}

.weather-detail-item:hover {
  color: #2d3436;
  transform: translateX(5px);
}

/* 动态图标效果 */
.weather-icon {
  font-size: 1.2em;
  transition: all 0.3s ease;
}

/* 风力图标动画 */
.wind-icon {
  animation: wind-blow 2s ease-in-out infinite;
}

@keyframes wind-blow {
  0%, 100% { transform: translateX(0) rotate(0deg); }
  25% { transform: translateX(2px) rotate(2deg); }
  50% { transform: translateX(-1px) rotate(-1deg); }
  75% { transform: translateX(1px) rotate(1deg); }
}

/* 湿度图标动画 */
.humidity-icon {
  animation: humidity-drop 3s ease-in-out infinite;
}

@keyframes humidity-drop {
  0%, 100% { transform: translateY(0) scale(1); }
  50% { transform: translateY(-2px) scale(1.1); }
}

/* 悬停时增强动画 */
.weather-detail-item:hover .wind-icon {
  animation-duration: 1s;
}

.weather-detail-item:hover .humidity-icon {
  animation-duration: 1.5s;
}

/* 主要天气图标动画 */
.main-weather-icon {
  font-size: 2.5em;
  animation: main-weather-float 4s ease-in-out infinite;
}

@keyframes main-weather-float {
  0%, 100% { transform: translateY(0) rotate(0deg) scale(1); }
  25% { transform: translateY(-5px) rotate(1deg) scale(1.05); }
  50% { transform: translateY(-3px) rotate(0deg) scale(1.02); }
  75% { transform: translateY(-7px) rotate(-1deg) scale(1.05); }
}

/* 悬停时主要图标增强动画 */
.weather-desc:hover .main-weather-icon {
  animation-duration: 2s;
  transform: scale(1.1);
}

/* 移动端响应式 */
@media (max-width: 767px) {
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
}
</style>
