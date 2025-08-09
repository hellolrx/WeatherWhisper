/**
 * 应用常量定义
 */

// 应用配置
export const APP_CONFIG = {
  name: '天语 · Weather Whisper',
  subtitle: '简洁纯净的天气查询',
  version: '1.0.0'
} as const

// 收藏城市配置
export const FAVORITES_CONFIG = {
  maxLimit: 10,
  storageKey: 'ww_favorites'
} as const

// 搜索配置
export const SEARCH_CONFIG = {
  debounceDelay: 500,
  maxOptions: 10,
  placeholder: '输入城市名，例如：北京'
} as const

// 天气预报配置
export const FORECAST_CONFIG = {
  hourly: {
    total: 24,
    defaultShow: 12,
    gridColumns: {
      desktop: 6,
      mobile: 4
    }
  },
  daily: {
    total: 7,
    gridColumns: {
      desktop: 7,
      mobile: 3
    }
  }
} as const

// 地理位置配置
export const GEOLOCATION_CONFIG = {
  timeout: 10000,
  maximumAge: 300000, // 5分钟缓存
  enableHighAccuracy: true
} as const

// 动画配置
export const ANIMATION_CONFIG = {
  transition: {
    duration: '0.3s',
    easing: 'ease'
  },
  weatherIcons: {
    wind: {
      duration: '2s',
      hoverDuration: '1s'
    },
    humidity: {
      duration: '3s',
      hoverDuration: '1.5s'
    },
    main: {
      duration: '4s',
      hoverDuration: '2s'
    }
  }
} as const

// 响应式断点
export const BREAKPOINTS = {
  mobile: '767px',
  tablet: '768px',
  desktop: '1024px',
  widescreen: '1440px'
} as const
