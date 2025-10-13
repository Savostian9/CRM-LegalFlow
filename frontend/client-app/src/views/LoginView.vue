<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="logo">
        <router-link to="/">LegalFlow</router-link>
      </div>
  <h2 class="auth-title">{{ $t('auth.login.welcome') }}</h2>
  <p class="auth-subtitle">{{ $t('auth.login.subtitle') }}</p>
      
      <form @submit.prevent="loginUser" class="auth-form">
        <div class="form-group">
          <label for="email">{{ $t('auth.fields.email') }}</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.5a5.5 5.5 0 0 1 3.096 10.047 9.005 9.005 0 0 1 5.9 8.19.75.75 0 0 1-1.496.065 7.505 7.505 0 0 0-15 0 .75.75 0 0 1-1.496-.065 9.005 9.005 0 0 1 5.9-8.19A5.5 5.5 0 0 1 12 2.5ZM8 8a4 4 0 1 0 8 0 4 4 0 0 0-8 0Z" /></svg>
            <input type="email" id="email" v-model="email" required placeholder="you@example.com" />
          </div>
        </div>
        
        <div class="form-group">
          <label for="password">{{ $t('auth.fields.password') }}</label>
          <div class="input-wrapper">
            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M18 1.5a2.25 2.25 0 0 1 2.25 2.25v5.379a2.25 2.25 0 0 1-.66 1.59l-5.34 5.34a2.25 2.25 0 0 1-1.59.66H7.5a2.25 2.25 0 0 1-2.25-2.25v-5.38a2.25 2.25 0 0 1 .66-1.59l5.34-5.34a2.25 2.25 0 0 1 1.59-.66h5.12ZM15 9.75a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z" /><path d="M16.5 22.5a2.25 2.25 0 0 1-2.25-2.25v-5.379a2.25 2.25 0 0 1 .66-1.59l5.34-5.34a2.25 2.25 0 0 1 1.59-.66h.12a2.25 2.25 0 0 1 2.25 2.25v5.38a2.25 2.25 0 0 1-.66 1.59l-5.34 5.34a2.25 2.25 0 0 1-1.59.66h-5.12a2.25 2.25 0 0 1-2.25-2.25V18a.75.75 0 0 1 1.5 0v2.25a.75.75 0 0 0 .75.75h5.12a.75.75 0 0 0 .53-.22l5.34-5.34a.75.75 0 0 0 .22-.53v-5.38a.75.75 0 0 0-.75-.75h-.12a.75.75 0 0 0-.53.22l-5.34 5.34a.75.75 0 0 0-.22.53V20.25a2.25 2.25 0 0 1-2.25 2.25Z" clip-rule="evenodd" /></svg>
            <input :type="passwordFieldType" id="password" v-model="password" required placeholder="••••••••" />
            <button type="button" @click="togglePasswordVisibility" class="password-toggle">
              <svg v-if="passwordFieldType === 'password'" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" /><path fill-rule="evenodd" d="M1.323 11.447C2.811 6.976 7.028 3.75 12 3.75c4.97 0 9.189 3.226 10.677 7.697a.75.75 0 0 1 0 .606C21.189 17.024 16.97 20.25 12 20.25c-4.97 0-9.189-3.226-10.677-7.697a.75.75 0 0 1 0-.606ZM12 19.5a8.25 8.25 0 0 0 7.824-5.991 8.25 8.25 0 0 0-15.648 0A8.25 8.25 0 0 0 12 19.5Z" clip-rule="evenodd" /></svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M3.28 2.22a.75.75 0 0 0-1.06 1.06l4.088 4.088a10.043 10.043 0 0 0-2.977 4.125C2.811 17.024 7.028 20.25 12 20.25c2.181 0 4.225-.66 5.954-1.822l2.71 2.71a.75.75 0 1 0 1.06-1.06L3.28 2.22ZM12 19.5a8.25 8.25 0 0 0 7.824-5.991 8.358 8.358 0 0 0-1.424-2.527l-1.34-1.34a3.001 3.001 0 0 0-4.04-4.04l-1.34-1.34A8.358 8.358 0 0 0 8.176 7.509 8.25 8.25 0 0 0 12 19.5Zm-2.65-8.494a4.502 4.502 0 0 1 6.115-6.115l-6.115 6.115Zm7.973 1.327a10.034 10.034 0 0 0-2.383-2.924C13.939 8.653 12.974 8.25 12 8.25a4.5 4.5 0 0 0-1.14.167l1.327 1.327a3.001 3.001 0 0 1 3.82 3.82l1.327 1.327C17.705 14.805 18 15.39 18 16.02a.75.75 0 0 1-.75.75h-.02a.75.75 0 0 1-.75-.75c0-.44-.22-.857-.614-1.181Z" clip-rule="evenodd" /></svg>
            </button>
          </div>
        </div>
        
        <transition name="fade">
          <div v-if="message" class="error-message">{{ message }}</div>
        </transition>
        
        <button type="submit" class="auth-button" :disabled="isLoading">
          {{ isLoading ? $t('auth.login.signingIn') : $t('auth.login.signIn') }}
        </button>
      </form>
      
      <div class="auth-links">
  <router-link to="/password-reset">{{ $t('auth.login.forgot') }}</router-link>
  <router-link to="/register">{{ $t('auth.login.create') }}</router-link>
      </div>

    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { loadBillingUsage } from '@/billing/usageStore.js';

export default {
  name: 'LoginView',
  components: { },
  data() {
    return {
      email: '',
      password: '',
      message: '',
      isLoading: false,
      passwordFieldType: 'password'
    };
  },
  methods: {
    async loginUser() {
      this.message = '';
      this.isLoading = true;
      try {
  const response = await axios.post('/api/login/', {
          email: this.email,
          password: this.password
        });
        
        localStorage.setItem('user-token', response.data.token);
        localStorage.setItem('user-id', response.data.user_id);
        
  // Загрузим trial/usage данные в фоне (не блокируя редирект)
  try { loadBillingUsage(true); } catch (e) { /* ignore */ }
  this.$router.push('/dashboard');
      } catch (error) {
        const data = error?.response?.data;
        if (data?.non_field_errors && data.non_field_errors.length) {
          const msg = String(data.non_field_errors[0] || '').toLowerCase();
          if (msg.includes('неверн') || msg.includes('invalid')) {
            this.message = this.$t('auth.login.invalidCredentials');
          } else if (msg.includes('не актив') || msg.includes('not activ')) {
            this.message = this.$t('auth.login.notActivated');
          } else if (msg.includes('укажит') || msg.includes('missing') || msg.includes('email') && msg.includes('парол')) {
            this.message = this.$t('auth.login.missingCredentials');
          } else {
            this.message = this.$t('auth.errors.generic');
          }
        } else if (typeof data?.detail === 'string') {
          const msg = data.detail.toLowerCase();
          if (msg.includes('неверн') || msg.includes('invalid')) {
            this.message = this.$t('auth.login.invalidCredentials');
          } else if (msg.includes('не актив') || msg.includes('not activ')) {
            this.message = this.$t('auth.login.notActivated');
          } else {
            this.message = this.$t('auth.errors.generic');
          }
        } else if (data?.email) {
          this.message = this.$t('auth.errors.emailPrefix', { msg: data.email[0] });
        } else if (data?.username) {
          this.message = this.$t('auth.errors.usernamePrefix', { msg: data.username[0] });
        } else if (data?.password) {
          this.message = this.$t('auth.errors.passwordPrefix', { msg: data.password[0] });
        } else {
          this.message = this.$t('auth.errors.cannotConnect');
        }
      } finally {
        this.isLoading = false;
      }
    },
    togglePasswordVisibility() {
      this.passwordFieldType = this.passwordFieldType === 'password' ? 'text' : 'password';
    }
  }
};
</script>

<style scoped>
/* Импорт шрифта и общие переменные */
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
  --background-color: #f7f9fc; /* Светло-серый фон */
  --white-color: #ffffff;
  --default-border-color: #cdd4de;
  --error-color: #d93025;
  --gradient-start: #6dd5ed;
  --gradient-end: #2193b0;
}

.auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
  background-color: var(--background-color); /* ИЗМЕНЕНИЕ */
}

/* ... Остальные стили остаются без изменений ... */

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
}

.auth-form {
  margin-top: 0;
}

.form-group {
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
  border: 1px solid var(--default-border-color); 
  border-radius: 8px;
  box-sizing: border-box;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.15);
}

.password-toggle {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  padding: 5px;
  color: #78909c;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s ease-out;
}

.password-toggle:hover {
  color: var(--dark-blue);
}

.password-toggle svg {
  width: 20px;
  height: 20px;
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

.error-message {
  text-align: center;
  color: var(--error-color);
  background-color: rgba(217, 48, 37, 0.1);
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 0.9em;
}

.auth-links {
  display: flex;
  justify-content: space-between;
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