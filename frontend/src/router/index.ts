import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const Dashboard = () => import('../views/Dashboard.vue')
const LoginPage = () => import('../views/LoginPage.vue')
const RegisterPage = () => import('../views/RegisterPage.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { 
      path: '/', 
      name: 'dashboard', 
      component: Dashboard,
      meta: { requiresAuth: false } // 天气主页不需要认证
    },
    { 
      path: '/login', 
      name: 'login', 
      component: LoginPage,
      meta: { requiresAuth: false }
    },
    { 
      path: '/register', 
      name: 'register', 
      component: RegisterPage,
      meta: { requiresAuth: false }
    }
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // 如果用户已登录且访问登录/注册页，重定向到主页
  if (authStore.isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    next({ name: 'dashboard' })
    return
  }
  
  next()
})

export default router


