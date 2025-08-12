<template>
  <div class="user-info">
    <div class="user-avatar">
      <div class="avatar-circle">
        {{ userInitials }}
      </div>
    </div>
    
    <div class="user-details">
      <div class="username">{{ user?.username || '访客用户' }}</div>
      <div class="user-email">{{ user?.email || '访客模式' }}</div>
      <div class="user-status">
        <span v-if="isAuthenticated" class="status-badge authenticated">
          <i class="status-icon">✓</i>
          已登录
        </span>
        <span v-else class="status-badge guest">
          <i class="status-icon">👤</i>
          访客模式
        </span>
      </div>
    </div>
    
    <div class="user-actions">
      <button
        v-if="isAuthenticated"
        @click="handleLogout"
        class="logout-btn"
        :disabled="isLoading"
      >
        <span v-if="isLoading" class="loading">登出中...</span>
        <span v-else>登出</span>
      </button>
      
      <button
        v-else
        @click="goToLogin"
        class="login-btn"
      >
        登录
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useAuth } from '../../composables/useAuth'

const router = useRouter()
const authStore = useAuthStore()
const { logout, isLoading } = useAuth()

// 计算属性
const user = computed(() => authStore.user)
const isAuthenticated = computed(() => authStore.isAuthenticated)
const isGuest = computed(() => authStore.isGuest)

// 用户头像首字母
const userInitials = computed(() => {
  if (user.value?.username) {
    return user.value.username.substring(0, 2).toUpperCase()
  }
  return '访'
})

// 处理登出
async function handleLogout() {
  await logout()
}

// 跳转到登录页
function goToLogin() {
  router.push('/login')
}
</script>

<style scoped>
.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.user-avatar {
  flex-shrink: 0;
}

.avatar-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.user-details {
  flex: 1;
  min-width: 0;
}

.username {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 0.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.authenticated {
  background: #d4edda;
  color: #155724;
}

.status-badge.guest {
  background: #f8f9fa;
  color: #6c757d;
}

.status-icon {
  font-style: normal;
  font-size: 0.8rem;
}

.user-actions {
  flex-shrink: 0;
}

.logout-btn,
.login-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn {
  background: #e74c3c;
  color: white;
}

.logout-btn:hover:not(:disabled) {
  background: #c0392b;
  transform: translateY(-1px);
}

.logout-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.login-btn {
  background: #3498db;
  color: white;
}

.login-btn:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

.loading {
  display: inline-block;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .user-info {
    flex-direction: column;
    text-align: center;
    gap: 0.75rem;
  }
  
  .user-details {
    text-align: center;
  }
  
  .user-actions {
    width: 100%;
  }
  
  .logout-btn,
  .login-btn {
    width: 100%;
    padding: 0.75rem 1rem;
  }
}
</style> 