<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="logo">
        <router-link to="/">LegalFlow</router-link>
      </div>
      <h2 class="auth-title">Сброс пароля</h2>
      <p class="auth-subtitle">Введите ваш email, и мы вышлем вам ссылку для восстановления доступа.</p>
      
      <form @submit.prevent="handlePasswordReset" class="auth-form">
        <div class="form-group">
          <label for="email">Email</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M1.5 8.67v8.58a3 3 0 0 0 3 3h15a3 3 0 0 0 3-3V8.67l-8.928 5.493a3 3 0 0 1-3.144 0L1.5 8.67Z" /><path d="M22.5 6.908V6.75a3 3 0 0 0-3-3h-15a3 3 0 0 0-3 3v.158l9.714 5.978a1.5 1.5 0 0 0 1.572 0L22.5 6.908Z" /></svg>
            <input type="email" id="email" v-model="email" required placeholder="your@email.com" />
          </div>
        </div>
        
        <transition name="fade">
          <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        </transition>
        <transition name="fade">
          <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
        </transition>
        
        <button type="submit" class="auth-button" :disabled="isLoading">
          {{ isLoading ? 'Отправка...' : 'Отправить ссылку' }}
        </button>
      </form>
      
      <div class="auth-links">
        <router-link to="/login">Вернуться ко входу</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'PasswordResetView',
  data() {
    return {
      email: '',
      isLoading: false,
      errorMessage: '',
      successMessage: ''
    };
  },
  methods: {
    async handlePasswordReset() {
      this.isLoading = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/password-reset/', {
          email: this.email
        });
        
        this.successMessage = response.data.message;
        this.email = ''; // Очищаем поле после успешной отправки

      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Произошла ошибка при отправке.';
      } finally {
        this.isLoading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Стили полностью идентичны стилям LoginView для единообразия */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

:root {
  --primary-color: #4A90E2;
  --primary-hover: #357ABD;
  --dark-blue: #2c3e50;
  --text-color: #5a6a7b;
  --background-color: #f7f9fc;
  --white-color: #ffffff;
  --border-color: #cdd4de;
  --error-color: #d93025;
  --success-color: #1e8e3e;
  --gradient-start: #6dd5ed;
  --gradient-end: #2193b0;
}

.auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  background-color: var(--background-color);
}

.auth-card {
  background: var(--white-color);
  padding: 40px 50px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 420px;
  animation: fadeInUp 0.7s ease-out;
}

.logo {
  text-align: center;
  margin-bottom: 25px;
}

.logo a {
  font-size: 28px;
  font-weight: 700;
  text-decoration: none;
  color: var(--dark-blue);
}

.auth-title, .auth-subtitle {
  text-align: center;
}

.auth-title {
    margin-bottom: 10px;
}

.auth-subtitle {
    margin-bottom: 35px;
    line-height: 1.5;
}

.auth-form .form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--dark-blue);
}

.input-wrapper {
  position: relative;
}

.form-group .input-icon {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: #90a4ae;
  pointer-events: none;
}

.form-group input {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid var(--border-color); 
  border-radius: 8px;
  box-sizing: border-box;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.15);
}

.auth-button {
  width: 100%;
  padding: 16px; 
  margin-top: 20px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(90deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
  color: var(--white-color);
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 8px 20px rgba(33, 147, 176, 0.3);
  transition: all 0.3s ease-out;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.auth-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 25px rgba(33, 147, 176, 0.4);
}

.auth-button:active {
  transform: translateY(0px) scale(0.98);
  box-shadow: 0 5px 15px rgba(33, 147, 176, 0.3);
}

.auth-button:disabled {
  background: #cfd8dc;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  color: #78909c;
}

.message-base {
  text-align: center;
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9em;
}

.error-message {
  color: var(--error-color);
  background-color: rgba(217, 48, 37, 0.1);
}

.success-message {
  color: var(--success-color);
  background-color: rgba(30, 142, 62, 0.1);
}

.auth-links {
  text-align: center; /* Центрируем одну ссылку */
  margin-top: 30px;
}

.auth-links a {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 500;
  font-size: 14px;
  transition: color 0.2s ease-out;
}
.auth-links a:hover {
  text-decoration: underline;
  color: var(--primary-hover);
}
</style>