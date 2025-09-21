<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <router-link to="/" class="logo">LegalFlow</router-link>
      </div>
      <div class="user-profile">
        <div class="avatar">{{ userInitials }}</div>
        <span class="username">{{ username }}</span>
      </div>
      <nav class="nav-links">
        <ul>
          <li><router-link to="/dashboard" class="active"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M10.5 18a.75.75 0 0 0 .75.75h1.5a.75.75 0 0 0 .75-.75v-3a.75.75 0 0 0-.75-.75h-1.5a.75.75 0 0 0-.75.75v3ZM9 6.75A.75.75 0 0 1 9.75 6h1.5a.75.75 0 0 1 .75.75v11.25a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75V6.75ZM5.25 9A.75.75 0 0 0 6 9.75v8.25a.75.75 0 0 0 .75.75h1.5a.75.75 0 0 0 .75-.75V9.75A.75.75 0 0 0 8.25 9h-1.5A.75.75 0 0 0 5.25 9ZM15 9.75A.75.75 0 0 1 15.75 9h1.5a.75.75 0 0 1 .75.75v8.25a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75V9.75Z" /></svg>Главная</router-link></li>
          <li><router-link to="/clients"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M4.5 6.375a4.125 4.125 0 1 1 8.25 0 4.125 4.125 0 0 1-8.25 0ZM14.25 8.625a3.375 3.375 0 1 1 6.75 0 3.375 3.375 0 0 1-6.75 0ZM1.5 19.125a7.125 7.125 0 0 1 14.25 0v.003l-.001.119a.75.75 0 0 1-.363.63l-2.693 1.5c-.23.128-.487.256-.737.38a1.71 1.71 0 0 0-.339.242l-1.843 1.843a.75.75 0 0 1-1.06 0l-1.843-1.843a1.71 1.71 0 0 0-.339-.242c-.25-.124-.507-.252-.737-.38l-2.694-1.5a.75.75 0 0 1-.362-.63V19.125ZM17.25 19.125a7.125 7.125 0 0 1 14.25 0v.003l-.001.119a.75.75 0 0 1-.363.63l-2.693 1.5c-.23.128-.487.256-.737.38a1.71 1.71 0 0 0-.339.242l-1.843 1.843a.75.75 0 0 1-1.06 0l-1.843-1.843a1.71 1.71 0 0 0-.339-.242c-.25-.124-.507-.252-.737-.38l-2.694-1.5a.75.75 0 0 1-.362-.63V19.125Z" /></svg>Клиенты</router-link></li>
          <li><router-link to="/cases"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M2.25 2.25a.75.75 0 0 0 0 1.5H3v10.5a3 3 0 0 0 3 3h1.21l-1.12 1.12a.75.75 0 0 0 1.06 1.06l1.5-1.5a.75.75 0 0 0 0-1.06l-1.5-1.5a.75.75 0 0 0-1.06 1.06l1.12 1.12H6a1.5 1.5 0 0 1-1.5-1.5V3.75h13.5v10.5a1.5 1.5 0 0 1-1.5 1.5H11.25a.75.75 0 0 0 0 1.5h4.25a3 3 0 0 0 3-3V3.75h.75a.75.75 0 0 0 0-1.5H2.25Z" clip-rule="evenodd" /></svg>Дела</router-link></li>
          <li><router-link to="/tasks"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M11.637 2.23a.75.75 0 0 1 .726 0l2.573 1.028a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5l-2.573-1.028a.75.75 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 .63-.5Zm6.93 4.2a.75.75 0 0 1 .63.5l1.286 2.573a.75.75 0 0 1-.5 1.13l-2.573 1.028a.75.75 0 0 1-1.13-.5l-1.286-2.573a.75.75 0 0 1 .5-1.13l2.573-1.028a.75.75 0 0 1 .5 0ZM6.08 6.43a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5L1.085 9.605a.75.75 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 1.13-.5l2.573 1.028a.75.75 0 0 1 .5 0Zm11.857 6.071a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5l-2.573-1.028a.75.T5 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 1.13-.5l2.573 1.028a.75.75 0 0 1 .5 0Zm-6.93 4.2a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5l-2.573-1.028a.75.75 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 1.13-.5l2.573 1.028a.75.75 0 0 1 .5 0Z" clip-rule="evenodd" /></svg>Задачи</router-link></li>
          <li><router-link to="/calendar"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12.75 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM7.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM8.25 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM9.75 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM10.5 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM12.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM14.25 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM15 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM12 10.5a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM13.5 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" /><path fill-rule="evenodd" d="M3.75 2.25A.75.75 0 0 1 3 3v18a.75.75 0 0 1-1.5 0V3a2.25 2.25 0 0 1 2.25-2.25h15A2.25 2.25 0 0 1 21 3v18a.75.75 0 0 1-1.5 0V3a.75.75 0 0 0-.75-.75h-15a.75.75 0 0 1-.75.75Z" clip-rule="evenodd" /></svg>Календарь</router-link></li>
          <li><router-link to="/settings"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M9.458 1.412A8.966 8.966 0 0 1 12 1.125c1.99 0 3.843.63 5.378 1.69l.405-1.71a.75.75 0 0 1 1.44.34l.053.224a.75.75 0 0 1-.34 1.44l-1.71.405a8.965 8.965 0 0 1 1.69 5.378l1.71.405a.75.75 0 0 1 .34 1.44l-.224.053a.75.75 0 0 1-1.44-.34l-.405-1.71a8.965 8.965 0 0 1-5.378 1.69l-.405 1.71a.75.75 0 0 1-1.44.34l-.053-.224a.75.75 0 0 1 .34-1.44l.405-1.71a8.966 8.966 0 0 1-5.378-1.69l-1.71-.405a.75.75 0 0 1-.34-1.44l.224-.053a.75.75 0 0 1 1.44.34l1.71.405A8.966 8.966 0 0 1 2.625 12c0-1.99.63-3.843 1.69-5.378L2.605 6.217a.75.75 0 0 1-.34-1.44l.224-.053a.75.75 0 0 1 1.44.34L5.64 5.472A8.966 8.966 0 0 1 9.458 1.412ZM12 8.25a3.75 3.75 0 1 0 0 7.5 3.75 3.75 0 0 0 0-7.5Z" clip-rule="evenodd" /></svg>Настройки</router-link></li>
        </ul>
      </nav>
      <div class="sidebar-footer">
        <button @click="logout" class="logout-button">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M7.5 3.75A1.5 1.5 0 0 0 6 5.25v13.5a1.5 1.5 0 0 0 1.5 1.5h6a1.5 1.5 0 0 0 1.5-1.5V15a.75.75 0 0 1 1.5 0v3.75a3 3 0 0 1-3 3h-6a3 3 0 0 1-3-3V5.25a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3V9A.75.75 0 0 1 15 9V5.25a1.5 1.5 0 0 0-1.5-1.5h-6Zm10.72 4.72a.75.75 0 0 1 1.06 0l3 3a.75.75 0 0 1 0 1.06l-3 3a.75.75 0 1 1-1.06-1.06l1.72-1.72H9a.75.75 0 0 1 0-1.5h10.94l-1.72-1.72a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" /></svg>
          Выйти
        </button>
      </div>
    </aside>

    <main class="main-content">
      <div v-if="loading" class="loader">Загрузка...</div>
      <div v-if="!loading" class="content-wrapper">
        <header class="content-header">
          <h1>Главная</h1>
        </header>
        <div class="content-body">
          <div class="welcome-card">
            <h2>Добро пожаловать, {{ username }}!</h2>
            <p>Это ваша отправная точка. Здесь будет сводка по всем вашим делам, документам и предстоящим задачам.</p>
          </div>
          </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ClientDashboardView',
  data() {
    return {
      username: '',
      loading: true,
    };
  },
  computed: {
    userInitials() {
      // Создаем инициалы для аватара
      return this.username ? this.username.charAt(0).toUpperCase() : '';
    }
  },
  async created() {
    const token = localStorage.getItem('user-token');
    if (!token) {
      this.$router.push('/login');
      return;
    }

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/user-info/', {
        headers: {
          Authorization: `Token ${token}`
        }
      });
      this.username = response.data.username;
    } catch (error) {
      console.error('Ошибка получения данных:', error);
      localStorage.removeItem('user-token'); // Очищаем невалидный токен
      this.$router.push('/login');
    } finally {
      this.loading = false;
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('user-token');
      localStorage.removeItem('user-id');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary-color: #4A90E2;
  --dark-blue: #2c3e50;
  --sidebar-bg: #1a202c;
  --sidebar-text: #a0aec0;
  --sidebar-text-hover: #ffffff;
  --background-color: #f7f9fc;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  padding: 20px;
  flex-shrink: 0;
}

.sidebar-header {
  margin-bottom: 30px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  text-decoration: none;
  color: var(--sidebar-text-hover);
}

.user-profile {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 600;
  margin-right: 15px;
}

.username {
  font-weight: 600;
  color: var(--sidebar-text-hover);
}

.nav-links ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-links li {
  margin-bottom: 10px;
}

.nav-links a {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  text-decoration: none;
  color: var(--sidebar-text);
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-links a svg {
  width: 20px;
  height: 20px;
  margin-right: 15px;
}

.nav-links a:hover, .nav-links a.active {
  background-color: var(--primary-color);
  color: var(--sidebar-text-hover);
}

.sidebar-footer {
  margin-top: auto; /* Прижимает кнопку выхода к низу */
}

.logout-button {
  width: 100%;
  padding: 12px;
  background: none;
  border: 1px solid rgba(255, 82, 82, 0.3);
  color: #ff5252;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s ease;
}

.logout-button svg {
  width: 20px;
  height: 20px;
  margin-right: 10px;
}

.logout-button:hover {
  background-color: rgba(255, 82, 82, 0.1);
  color: #ff8a80;
  border-color: rgba(255, 82, 82, 0.5);
}


/* Main Content */
.main-content {
  flex-grow: 1;
  background-color: var(--background-color);
  padding: 40px;
}

.content-header {
  margin-bottom: 30px;
}

.content-header h1 {
  font-size: 28px;
  color: var(--dark-blue);
  font-weight: 700;
}

.welcome-card {
  background-color: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}

.welcome-card h2 {
  font-size: 24px;
  color: var(--dark-blue);
  margin-top: 0;
}
</style>