<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <h2 class="auth-title">Подтверждение Email</h2>
      <p class="info-text">
        Мы отправили 6-значный код на <strong>{{ email }}</strong>
      </p>
      
      <form @submit.prevent="handleVerification" class="auth-form">
        <div class="form-group">
          <label for="token">Код подтверждения</label>
          <input type="text" id="token" v-model="token" required maxlength="6" pattern="\d{6}" placeholder="------" />
        </div>
        
        <button type="submit" class="auth-button">Подтвердить</button>

        <div v-if="message" :class="isError ? 'error-message' : 'success-message'">{{ message }}</div>
      </form>
      
      <div class="resend-container">
        <span v-if="timer > 0">Отправить код повторно можно через: {{ timer }} сек.</span>
        <button v-else @click="resendCode" class="resend-button">Отправить код еще раз</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

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
    // Получаем email из параметров URL при загрузке страницы
    this.email = this.$route.query.email || 'вашу почту';
  },
  mounted() {
    this.startTimer();
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
        // ИСПРАВЛЕННЫЙ URL
        const response = await axios.post('http://127.0.0.1:8000/api/verify-email/', {
          email: this.email,
          token: this.token
        });

        this.message = response.data.message;
        // Через 2 секунды перенаправляем на страницу входа
        setTimeout(() => {
          this.$router.push('/login');
        }, 2000);

      } catch (err) {
        this.isError = true;
        this.message = err.response?.data?.error || 'Произошла ошибка.';
      }
    },
    async resendCode() {
        if (this.timer > 0) return; // Не даем отправлять, пока таймер не истек

        this.message = '';
        this.isError = false;
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/resend-verify-email/', {
                email: this.email
            });
            this.message = response.data.message;
            this.startTimer(); // Перезапускаем таймер
        } catch (err) {
            this.isError = true;
            this.message = err.response?.data?.error || 'Ошибка при повторной отправке.';
        }
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
.resend-button {
    background: none;
    border: none;
    color: #007bff;
    text-decoration: underline;
    cursor: pointer;
}
.error-message {
    color: #d93025;
    margin-top: 15px;
}
.success-message {
    color: #1e8e3e;
    margin-top: 15px;
}
</style>