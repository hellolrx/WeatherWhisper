<template>
  <div class="register-form">
    <div class="form-header">
      <h2>用户注册</h2>
      <p>创建账号后可以收藏城市和享受更多功能</p>
    </div>

    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <form @submit.prevent="handleSubmit" class="form">
      <!-- 邮箱输入 -->
      <div class="form-group">
        <label for="email">邮箱地址</label>
        <input
          id="email"
          v-model="formData.email"
          type="email"
          placeholder="请输入邮箱地址"
          :class="{ 'error': formErrors.email }"
          @blur="validateField('email')"
        />
        <span v-if="formErrors.email" class="error-text">{{ formErrors.email }}</span>
      </div>

      <!-- 用户名输入 -->
      <div class="form-group">
        <label for="username">用户名</label>
        <input
          id="username"
          v-model="formData.username"
          type="text"
          placeholder="请输入用户名"
          :class="{ 'error': formErrors.username }"
          @blur="validateField('username')"
        />
        <span v-if="formErrors.username" class="error-text">{{ formErrors.username }}</span>
      </div>

      <!-- 密码输入 -->
      <div class="form-group">
        <label for="password">密码</label>
        <input
          id="password"
          v-model="formData.password"
          type="password"
          placeholder="请输入密码（至少8位）"
          :class="{ 'error': formErrors.password }"
          @blur="validateField('password')"
        />
        <span v-if="formErrors.password" class="error-text">{{ formErrors.password }}</span>
      </div>

      <!-- 确认密码输入 -->
      <div class="form-group">
        <label for="confirmPassword">确认密码</label>
        <input
          id="confirmPassword"
          v-model="formData.confirmPassword"
          type="password"
          placeholder="请再次输入密码"
          :class="{ 'error': formErrors.confirmPassword }"
          @blur="validateField('confirmPassword')"
        />
        <span v-if="formErrors.confirmPassword" class="error-text">{{ formErrors.confirmPassword }}</span>
      </div>

      <!-- 提交按钮 -->
      <button
        type="submit"
        class="submit-btn"
        :disabled="isLoading"
      >
        <span v-if="isLoading" class="loading">注册中...</span>
        <span v-else>立即注册</span>
      </button>

      <!-- 其他选项 -->
      <div class="form-footer">
        <div class="links">
          <router-link to="/login" class="link">已有账号？立即登录</router-link>
        </div>
        <div class="guest-mode">
          <button
            type="button"
            class="guest-btn"
            @click="enableGuestMode"
            :disabled="isLoading"
          >
            访客模式
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { useAuth } from '../../composables/useAuth'
import type { UserCreate } from '../../types/auth'

// 使用认证组合式API
const {
  register,
  enableGuestMode,
  isLoading,
  error,
  formErrors,
  clearErrors,
  registerValidationRules
} = useAuth()

// 表单数据
const formData = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

// 表单提交处理
async function handleSubmit() {
  // 清除之前的错误
  clearErrors()
  
  // 验证表单
  if (!validateForm()) {
    return
  }
  
  // 构建注册数据
  const userData: UserCreate = {
    email: formData.email,
    username: formData.username,
    password: formData.password
  }
  
  // 提交注册
  const success = await register(userData)
  if (success) {
    // 注册成功，跳转由useAuth处理
    console.log('注册成功')
  }
}

// 表单验证
function validateForm(): boolean {
  let isValid = true
  
  // 验证邮箱
  const emailError = registerValidationRules.email(formData.email)
  if (emailError) {
    formErrors.email = emailError
    isValid = false
  }
  
  // 验证用户名
  const usernameError = registerValidationRules.username(formData.username)
  if (usernameError) {
    formErrors.username = usernameError
    isValid = false
  }
  
  // 验证密码
  const passwordError = registerValidationRules.password(formData.password)
  if (passwordError) {
    formErrors.password = passwordError
    isValid = false
  }
  
  // 验证确认密码
  const confirmPasswordError = registerValidationRules.confirmPassword(formData.confirmPassword, formData)
  if (confirmPasswordError) {
    formErrors.confirmPassword = confirmPasswordError
    isValid = false
  }
  
  return isValid
}

// 字段验证
function validateField(field: string) {
  if (field === 'email') {
    const error = registerValidationRules.email(formData.email)
    formErrors.email = error || ''
  } else if (field === 'username') {
    const error = registerValidationRules.username(formData.username)
    formErrors.username = error || ''
  } else if (field === 'password') {
    const error = registerValidationRules.password(formData.password)
    formErrors.password = error || ''
  } else if (field === 'confirmPassword') {
    const error = registerValidationRules.confirmPassword(formData.confirmPassword, formData)
    formErrors.confirmPassword = error || ''
  }
}
</script>

<style scoped>
.register-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.75rem;
  font-weight: 600;
}

.form-header p {
  color: #7f8c8d;
  margin: 0;
  font-size: 0.9rem;
}

.error-message {
  background: #fee;
  color: #c53030;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid #fed7d7;
  font-size: 0.9rem;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  color: #2c3e50;
  font-weight: 500;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.form-group input {
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: all 0.2s ease;
  background: white;
}

.form-group input:focus {
  outline: none;
  border-color: #27ae60;
  box-shadow: 0 0 0 3px rgba(39, 174, 96, 0.1);
}

.form-group input.error {
  border-color: #e74c3c;
}

.error-text {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.submit-btn {
  background: linear-gradient(135deg, #27ae60, #229954);
  color: white;
  border: none;
  padding: 0.875rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 0.5rem;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading {
  display: inline-block;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.form-footer {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
  text-align: center;
}

.links {
  margin-bottom: 0.5rem;
}

.link {
  color: #27ae60;
  text-decoration: none;
  font-size: 0.9rem;
  transition: color 0.2s ease;
}

.link:hover {
  color: #229954;
  text-decoration: underline;
}

.guest-mode {
  border-top: 1px solid #e2e8f0;
  padding-top: 1rem;
}

.guest-btn {
  background: transparent;
  color: #7f8c8d;
  border: 2px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.guest-btn:hover:not(:disabled) {
  border-color: #bdc3c7;
  color: #2c3e50;
  background: #f8f9fa;
}

.guest-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-form {
    margin: 1rem;
    padding: 1.5rem;
  }
  
  .form-header h2 {
    font-size: 1.5rem;
  }
}
</style> 