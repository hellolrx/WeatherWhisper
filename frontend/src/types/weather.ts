/**
 * 天气应用相关的类型定义
 */

// 城市选项类型
export interface CityOption {
  id: string
  name: string
  adm1?: string  // 省份
  adm2?: string  // 市级行政区
  fullName?: string
}

// 当前天气数据类型
export interface CurrentWeather {
  now: {
    temp: string
    icon: string
    text: string
    windDir: string
    windScale: string
    humidity: string
    [key: string]: any
  }
  updateTime: string
  [key: string]: any
}

// 小时预报数据类型
export interface HourlyWeather {
  fxTime: string
  temp: string
  icon: string
  text: string
  [key: string]: any
}

// 日预报数据类型
export interface DailyWeather {
  fxDate: string
  tempMax: string
  tempMin: string
  iconDay: string
  textDay: string
  [key: string]: any
}

// 收藏城市类型（从store中导入）
export interface FavoriteCity {
  id: string
  name: string
  adm1?: string
  adm2?: string
}
