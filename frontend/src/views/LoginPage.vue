<template>
  <div class="login-page">
    <div class="page-background">
      <div class="background-overlay"></div>
    </div>
    
    <div class="page-content">
      <div class="logo-section">
        <h1 class="app-title">WeatherWhisper</h1>
        <p class="app-subtitle">天语 - 智能天气助手</p>
      </div>
      
      <div class="form-section">
        <LoginForm />
      </div>
      
      <div class="footer-section">
        <p class="footer-text">© 2025 WeatherWhisper. 让天气信息触手可及</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LoginForm from '../components/auth/LoginForm.vue'
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.page-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #74b9ff 0%, #0984e3 50%, #6c5ce7 100%);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

.background-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  z-index: 1;
}

.logo-section {
  text-align: center;
  margin-bottom: 3rem;
}

.app-title {
  font-size: 3rem;
  font-weight: 700;
  color: white;
  margin: 0 0 0.5rem 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  letter-spacing: 2px;
}

.app-subtitle {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
  font-weight: 300;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.form-section {
  width: 100%;
  max-width: 450px;
  margin-bottom: 2rem;
}

.footer-section {
  text-align: center;
}

.footer-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  margin: 0;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }
  
  .app-title {
    font-size: 2.5rem;
  }
  
  .app-subtitle {
    font-size: 1rem;
  }
  
  .logo-section {
    margin-bottom: 2rem;
  }
}

@media (max-width: 480px) {
  .app-title {
    font-size: 2rem;
  }
  
  .app-subtitle {
    font-size: 0.9rem;
  }
}
</style> 