/**
 * 通用工具函数
 */

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param wait 等待时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: number | null = null
  
  return function (this: any, ...args: Parameters<T>) {
    const context = this
    
    if (timeout !== null) {
      clearTimeout(timeout)
    }
    
    timeout = setTimeout(() => {
      func.apply(context, args)
    }, wait)
  }
}

/**
 * 节流函数
 * @param func 要节流的函数
 * @param wait 等待时间（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: number | null = null
  let previous = 0
  
  return function (this: any, ...args: Parameters<T>) {
    const context = this
    const now = Date.now()
    
    if (!previous) previous = now
    const remaining = wait - (now - previous)
    
    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout)
        timeout = null
      }
      previous = now
      func.apply(context, args)
    } else if (!timeout) {
      timeout = setTimeout(() => {
        previous = Date.now()
        timeout = null
        func.apply(context, args)
      }, remaining)
    }
  }
}

/**
 * 格式化日期时间
 * @param date 日期对象或日期字符串
 * @param format 格式化类型
 * @returns 格式化后的字符串
 */
export function formatDateTime(
  date: Date | string,
  format: 'date' | 'time' | 'datetime' = 'datetime'
): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date
  
  if (format === 'date') {
    return dateObj.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }
  
  if (format === 'time') {
    return dateObj.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }
  
  return dateObj.toLocaleString('zh-CN')
}

/**
 * 深度克隆对象
 * @param obj 要克隆的对象
 * @returns 克隆后的对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T
  }
  
  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as T
  }
  
  if (typeof obj === 'object') {
    const clonedObj = {} as T
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key])
      }
    }
    return clonedObj
  }
  
  return obj
}

/**
 * 检查是否为移动设备
 * @returns 是否为移动设备
 */
export function isMobile(): boolean {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  )
}

/**
 * 获取视口尺寸
 * @returns 视口宽度和高度
 */
export function getViewportSize(): { width: number; height: number } {
  return {
    width: window.innerWidth || document.documentElement.clientWidth,
    height: window.innerHeight || document.documentElement.clientHeight
  }
}

/**
 * 滚动到指定元素
 * @param element 目标元素
 * @param behavior 滚动行为
 */
export function scrollToElement(
  element: HTMLElement,
  behavior: ScrollBehavior = 'smooth'
): void {
  element.scrollIntoView({
    behavior,
    block: 'center',
    inline: 'nearest'
  })
}
