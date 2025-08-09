<script setup lang="ts">
import { ref, defineEmits, defineProps } from 'vue'
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
}>()

// Local state
const query = ref('')
const searchTimeout = ref<number | null>(null)

// Methods
function handleInput() {
  if (searchTimeout.value) clearTimeout(searchTimeout.value)
  if (!query.value.trim()) {
    emit('closeOptions')
    return
  }
  
  searchTimeout.value = setTimeout(() => {
    emit('input', query.value)
  }, 500)
}

function handleSearch() {
  if (query.value.trim()) {
    emit('search', query.value)
  }
}

function handleSelectCity(city: CityOption) {
  query.value = city.name
  emit('selectCity', city)
}

function handleKeyup(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    handleSearch()
  }
}

function handleFocus() {
  if (props.options.length > 1) {
    // 这里应该emit showOptions事件，但为了简化先直接处理
  }
}

function handleBlur() {
  // 延迟关闭，避免点击选项时立即关闭
  setTimeout(() => {
    emit('closeOptions')
  }, 150)
}
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
          placeholder="输入城市名，例如：北京" 
          @input="handleInput"
          @keyup="handleKeyup"
          @focus="handleFocus"
          @blur="handleBlur"            
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
      
      <!-- 搜索结果下拉 -->
      <Transition name="dropdown">
        <div v-if="showOptions && options.length > 1" class="options-dropdown">
          <div class="dropdown-header">
            <span>选择城市</span>
            <button @click="emit('closeOptions')" class="close-btn">✕</button>
          </div>
          <div 
            v-for="opt in options" 
            :key="opt.id" 
            @click="handleSelectCity(opt)"
            class="option-item"
          >
            📍 {{ opt.fullName }}
          </div>
        </div>
      </Transition>
    </div>

    <!-- 错误提示 -->
    <div v-if="errorMsg" class="error-message">
      ⚠️ {{ errorMsg }}
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
</style>
