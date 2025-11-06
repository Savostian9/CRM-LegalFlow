<template>
  <div class="auth-wrapper">
    <div class="auth-card">
  <h2 class="auth-title">{{ $t('auth.verify.title') }}</h2>
      <p class="info-text">
  {{ $t('auth.verify.sent') }} <strong>{{ email }}</strong>
      </p>
      
      <form @submit.prevent="handleVerification" class="auth-form">
        <div class="form-group">
          <label for="token">{{ $t('auth.verify.codeLabel') }}</label>
          <input type="text" id="token" v-model="token" required maxlength="6" pattern="\d{6}" placeholder="------"
                 @invalid="onCodeInvalid" @input="onCodeInput" />
        </div>
        
  <button type="submit" class="auth-button">{{ $t('auth.verify.confirm') }}</button>

        <div v-if="message" :class="isError ? 'error-message' : 'success-message'">{{ message }}</div>
      </form>
      
      <div class="resend-container">
          <span v-if="timer > 0" class="resend-timer">{{ $t('auth.verify.resendIn') }} {{ timer }} {{ $t('auth.verify.sec') }}</span>
    <button v-else type="button" @click="resendCode" class="resend-button" :aria-label="$t('auth.verify.resend')">
            <svg class="resend-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 5a7 7 0 1 1-6.938 6H3a9 9 0 1 0 2.638-6.364V3.5a.5.5 0 0 0-.854-.353L1.5 6.432a.5.5 0 0 0 0 .707l3.284 3.285A.5.5 0 0 0 5.64 10V7.5A7 7 0 0 1 12 5Z"/></svg>
            {{ $t('auth.verify.resend') }}
          </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios-setup.js';

export default {
  name: 'VerifyEmailView',
  data() {
    return {
      token: '',
      email: '',
      message: '',
      isError: false,
      timer: 60, // 60 секунд на таймер
    };
  },
  created() {
  // Get email from URL query on load
  this.email = (this.$route.query.email || '').toLowerCase();
  // Pre-fill token from query if present
  if (this.$route.query.token) {
    this.token = String(this.$route.query.token).trim();
  }
  },
  mounted() {
    this.startTimer();
    // If token is present in URL, auto-verify
    if (this.email && this.token) {
      this.handleVerification();
    }
  },
  methods: {
    startTimer() {
      this.timer = 60;
      const interval = setInterval(() => {
        if (this.timer > 0) {
          this.timer--;
        } else {
          clearInterval(interval);
        }
      }, 1000);
    },
    async handleVerification() {
      this.message = '';
      this.isError = false;

      try {
  // Verified endpoint
        const response = await axios.post('/api/verify-email/', {
          email: this.email,
          token: this.token
        });

        this.message = response.data.message;
  // After 2 seconds redirect to login
        setTimeout(() => {
          this.$router.push('/login');
        }, 2000);

      } catch (err) {
        this.isError = true;
        const raw = err.response?.data?.error || '';
        const lower = String(raw).toLowerCase();
        if (lower.includes('invalid') || lower.includes('неверн')) {
          this.message = this.$t('auth.verify.invalidToken');
        } else {
          this.message = raw || this.$t('auth.common.error');
        }
      }
    },
    async resendCode() {
        if (this.timer > 0) return; // Не даем отправлять, пока таймер не истек

        this.message = '';
        this.isError = false;
        try {
    await axios.post('/api/resend-verify-email/', {
                email: this.email
            });
      // Покажем локализованное дружелюбное сообщение вместо серверной строки
      this.message = this.$t('auth.verify.sentToast');
            this.startTimer(); // Перезапускаем таймер
        } catch (err) {
            this.isError = true;
            this.message = err.response?.data?.error || this.$t('auth.verify.resendError');
        }
    }
    ,onCodeInvalid(e){
      try{
        const t = e?.target; if(!t) return;
        const v = t.validity || {};
        if (v.valueMissing) t.setCustomValidity(this.$t('auth.verify.codeRequired'));
        else if (v.patternMismatch) t.setCustomValidity(this.$t('auth.verify.codeInvalid'));
      }catch{/* noop */}
    }
    ,onCodeInput(e){
      try{
        const t = e?.target; if(!t) return;
        const v = t.validity || {};
        if (v.valid) { t.setCustomValidity(''); return; }
        if (v.valueMissing) t.setCustomValidity(this.$t('auth.verify.codeRequired'));
        else if (v.patternMismatch) t.setCustomValidity(this.$t('auth.verify.codeInvalid'));
      }catch{/* noop */}
    }
  }
}
</script>

<style scoped>
.auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f4f7f6;
}
.auth-card {
  background: white;
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}
.auth-title {
  margin-bottom: 20px;
  font-size: 24px;
}
.info-text {
  margin-bottom: 30px;
  color: #555;
  line-height: 1.5;
}
.form-group label {
  display: none; /* Скрываем label, т.к. есть placeholder и заголовок */
}
.form-group input {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
  box-sizing: border-box;
  text-align: center;
  font-size: 1.5em;
  letter-spacing: 0.5em; /* Расстояние между символами */
}
.auth-button {
  width: 100%;
  padding: 12px;
  margin-top: 10px;
  border: none;
  border-radius: 5px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  font-size: 16px;
}
.resend-container {
    margin-top: 25px;
    color: #666;
}
.resend-timer { color: #666; }
.resend-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1px solid #e3f2fd;
  color: #1e88e5;
  padding: 8px 12px;
  border-radius: 999px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color .2s ease, box-shadow .2s ease, color .2s ease;
}
.resend-button:hover {
  background: #e3f2fd;
  box-shadow: 0 2px 8px rgba(30,136,229,.15);
}
.resend-button:active {
  background: #d6ecff;
}
.resend-icon { width: 18px; height: 18px; }
.error-message {
    color: #d93025;
    margin-top: 15px;
}
.success-message {
    color: #1e8e3e;
    margin-top: 15px;
}
</style>