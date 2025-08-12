import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
// 导入全局样式
import './styles/global.css'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// 初始化认证状态
import { useAuthStore } from './stores/auth'
const authStore = useAuthStore()
authStore.initAuth()

app.mount('#app')
