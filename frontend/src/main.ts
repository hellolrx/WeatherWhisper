import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
// 导入全局样式
import './styles/global.css'
import App from './App.vue'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
