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

    <!-- 成功提示 -->
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>

    <form @submit.prevent="handleSubmit" class="form">
      <!-- 邮箱输入 -->
      <div class="form-group">
        <label for="email">邮箱地址</label>
        <div class="email-input-group">
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="请输入邮箱地址"
            :class="{ 'error': formErrors.email }"
            @blur="validateField('email')"
            :disabled="isLoading"
          />
          <button
            type="button"
            class="send-code-btn"
            @click="sendVerificationCode"
            :disabled="isLoading || !formData.email || countdown > 0"
          >
            <span v-if="countdown > 0">{{ countdown }}s</span>
            <span v-else>发送验证码</span>
          </button>
        </div>
        <span v-if="formErrors.email" class="error-text">{{ formErrors.email }}</span>
      </div>

      <!-- 验证码输入 -->
      <div class="form-group">
        <label for="verificationCode">验证码</label>
        <input
          id="verificationCode"
          v-model="formData.verificationCode"
          type="text"
          placeholder="请输入6位验证码"
          maxlength="6"
          :class="{ 'error': formErrors.verificationCode }"
          @blur="validateField('verificationCode')"
          :disabled="isLoading"
        />
        <span v-if="formErrors.verificationCode" class="error-text">{{ formErrors.verificationCode }}</span>
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
          :disabled="isLoading"
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
          :disabled="isLoading"
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
          :disabled="isLoading"
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
import { reactive, ref } from 'vue'
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
  confirmPassword: '',
  verificationCode: ''
})

// 状态管理
const successMessage = ref('')
const countdown = ref(0)

// 发送验证码
async function sendVerificationCode() {
  if (!formData.email) {
    formErrors.email = '请先输入邮箱地址'
    return
  }
  
  // 验证邮箱格式
  const emailError = registerValidationRules.email(formData.email)
  if (emailError) {
    formErrors.email = emailError
    return
  }
  
  try {
    clearErrors()
    isLoading.value = true
    
    const response = await fetch('http://127.0.0.1:8000/api/auth/send-verification', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: formData.email,
        verification_type: 'register'
      }),
    })

    const data = await response.json()

    if (response.ok && data.success) {
      successMessage.value = data.message
      startCountdown()
      // 3秒后清除成功消息
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    } else {
      setError(data.message || '发送验证码失败')
    }

  } catch (err) {
    console.error('发送验证码失败:', err)
    setError('网络错误，请检查网络连接')
  } finally {
    isLoading.value = false
  }
}

// 开始倒计时
function startCountdown() {
  countdown.value = 60
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 设置错误
function setError(message: string) {
  error.value = message
}

// 表单提交处理
async function handleSubmit() {
  // 清除之前的错误
  clearErrors()
  successMessage.value = ''
  
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
  
  // 提交注册（带验证码）
  const success = await register(userData, formData.verificationCode)
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
  
  // 验证验证码
  if (!formData.verificationCode) {
    formErrors.verificationCode = '请输入验证码'
    isValid = false
  } else if (!/^[0-9]{6}$/.test(formData.verificationCode)) {
    formErrors.verificationCode = '验证码格式错误'
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
  } else if (field === 'verificationCode') {
    if (!formData.verificationCode) {
      formErrors.verificationCode = '请输入验证码'
    } else if (!/^[0-9]{6}$/.test(formData.verificationCode)) {
      formErrors.verificationCode = '验证码格式错误'
    } else {
      formErrors.verificationCode = ''
    }
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

.success-message {
  background: #f0fff4;
  color: #2f855a;
  padding: 0.75rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border: 1px solid #c6f6d5;
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

.email-input-group {
  display: flex;
  gap: 0.5rem;
}

.email-input-group input {
  flex: 1;
}

.send-code-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
  min-width: 100px;
}

.send-code-btn:hover:not(:disabled) {
  background: #2980b9;
}

.send-code-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
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

.form-group input:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
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
  
  .email-input-group {
    flex-direction: column;
  }
  
  .send-code-btn {
    min-width: auto;
  }
}
</style> 