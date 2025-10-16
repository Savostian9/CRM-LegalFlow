<template>
  <div class="dashboard-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
  <router-link :to="{ name: 'dashboard' }" class="logo">{{ $t('app.name') }}</router-link>
      </div>
      <div class="user-profile">
  <div class="avatar">{{ userInitials }}</div>
  <span class="username" :title="displayName">{{ displayName }}</span>
      </div>
      <nav class="nav-links">
        <ul>
          <li>
            <router-link
              to="/dashboard"
              :class="{ active: $route.path === '/dashboard' }"
              active-class="noop"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M10.5 18a.75.75 0 0 0 .75.75h1.5a.75.75 0 0 0 .75-.75v-3a.75.75 0 0 0-.75-.75h-1.5a.75.75 0 0 0-.75.75v3ZM9 6.75A.75.75 0 0 1 9.75 6h1.5a.75.75 0 0 1 .75.75v11.25a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75V6.75ZM5.25 9A.75.75 0 0 0 6 9.75v8.25a.75.75 0 0 0 .75.75h1.5a.75.75 0 0 0 .75-.75V9.75A.75.75 0 0 0 8.25 9h-1.5A.75.75 0 0 0 5.25 9ZM15 9.75A.75.75 0 0 1 15.75 9h1.5a.75.75 0 0 1 .75.75v8.25a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75V9.75Z" /></svg>
              <span>{{ $t('nav.dashboard') }}</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/dashboard/clients"
              :class="{ active: $route.path.startsWith('/dashboard/clients') }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M4.5 6.375a4.125 4.125 0 1 1 8.25 0 4.125 4.125 0 0 1-8.25 0ZM14.25 8.625a3.375 3.375 0 1 1 6.75 0 3.375 3.375 0 0 1-6.75 0ZM1.5 19.125a7.125 7.125 0 0 1 14.25 0v.003l-.001.119a.75.75 0 0 1-.363.63l-2.693 1.5c-.23.128-.487.256-.737.38a1.71 1.71 0 0 0-.339.242l-1.843 1.843a.75.75 0 0 1-1.06 0l-1.843-1.843a1.71 1.71 0 0 0-.339-.242c-.25-.124-.507-.252-.737-.38l-2.694-1.5a.75.75 0 0 1-.362-.63V19.125ZM17.25 19.125a7.125 7.125 0 0 1 14.25 0v.003l-.001.119a.75.75 0 0 1-.363.63l-2.693 1.5c-.23.128-.487.256-.737.38a1.71 1.71 0 0 0-.339.242l-1.843 1.843a.75.75 0 0 1-1.06 0l-1.843-1.843a1.71 1.71 0 0 0-.339-.242c-.25-.124-.507-.252-.737-.38l-2.694-1.5a.75.75 0 0 1-.362-.63V19.125Z" /></svg>
              <span>{{ $t('nav.clients') }}</span>
            </router-link>
          </li>
          <li v-if="role !== 'ASSISTANT'">
            <router-link
              to="/dashboard/finance"
              :class="{ active: $route.path.startsWith('/dashboard/finance') }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M3.75 4.5A2.25 2.25 0 0 0 1.5 6.75v10.5A2.25 2.25 0 0 0 3.75 19.5h16.5a2.25 2.25 0 0 0 2.25-2.25V6.75A2.25 2.25 0 0 0 20.25 4.5H3.75Zm0 1.5h16.5a.75.75 0 0 1 .75.75v1.5H3v-1.5a.75.75 0 0 1 .75-.75ZM3 9.75h18v7.5a.75.75 0 0 1-.75.75H3.75a.75.75 0 0 1-.75-.75v-7.5Zm3 2.25a.75.75 0 0 0 0 1.5h3a.75.75 0 0 0 0-1.5H6Zm0 3a.75.75 0 0 0 0 1.5h6a.75.75 0 0 0 0-1.5H6Z"/></svg>
              <span>{{ $t('nav.finance') }}</span>
            </router-link>
          </li>
          
          <li>
            <router-link
              to="/dashboard/tasks"
              :class="{ active: $route.path.startsWith('/dashboard/tasks') }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M11.637 2.23a.75.75 0 0 1 .726 0l2.573 1.028a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5l-2.573-1.028a.75.75 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 .63-.5Zm6.93 4.2a.75.75 0 0 1 .63.5l1.286 2.573a.75.75 0 0 1-.5 1.13l-2.573 1.028a.75.75 0 0 1-1.13-.5l-1.286-2.573a.75.75 0 0 1 .5-1.13l2.573-1.028a.75.75 0 0 1 .5 0ZM6.08 6.43a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5L1.085 9.605a.75.75 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 1.13-.5l2.573 1.028a.75.75 0 0 1 .5 0Zm11.857 6.071a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5l-2.573-1.028a.75.75 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 1.13-.5l2.573 1.028a.75.75 0 0 1 .5 0Zm-6.93 4.2a.75.75 0 0 1 .5 1.13l-1.286 2.573a.75.75 0 0 1-1.13.5l-2.573-1.028a.75.75 0 0 1-.5-1.13l1.286-2.573a.75.75 0 0 1 1.13-.5l2.573 1.028a.75.75 0 0 1 .5 0Z" clip-rule="evenodd" /></svg>
              <span>{{ $t('nav.tasks') }}</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/dashboard/calendar"
              :class="{ active: $route.path.startsWith('/dashboard/calendar') }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12.75 12.75a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM7.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM8.25 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM9.75 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM10.5 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM12 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM12.75 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM14.25 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM15 12a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM16.5 15.75a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5ZM12 10.5a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0ZM13.5 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" /><path fill-rule="evenodd" d="M3.75 2.25A.75.75 0 0 1 3 3v18a.75.75 0 0 1-1.5 0V3a2.25 2.25 0 0 1 2.25-2.25h15A2.25 2.25 0 0 1 21 3v18a.75.75 0 0 1-1.5 0V3a.75.75 0 0 0-.75-.75h-15a.75.75 0 0 1-.75.75Z" clip-rule="evenodd" /></svg>
              <span>{{ $t('nav.calendar') }}</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/dashboard/notifications"
              :class="{ active: $route.path.startsWith('/dashboard/notifications') }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M5.25 9a6.75 6.75 0 1 1 13.5 0v2.477c0 .51.113 1.014.332 1.474l1.05 2.153a1.5 1.5 0 0 1-1.35 2.146H5.218a1.5 1.5 0 0 1-1.35-2.146l1.05-2.153a3.375 3.375 0 0 0 .332-1.474V9Zm6.75 12a3.75 3.75 0 0 0 3.53-2.5H8.47a3.75 3.75 0 0 0 3.53 2.5Z"/></svg>
              <span class="notif-label">{{ $t('nav.notifications') || 'Уведомления' }}<span v-if="unreadCount" class="badge">{{ unreadCount }}</span></span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/dashboard/settings"
              :class="{ active: $route.path.startsWith('/dashboard/settings') }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M9.458 1.412A8.966 8.966 0 0 1 12 1.125c1.99 0 3.843.63 5.378 1.69l.405-1.71a.75.75 0 0 1 1.44.34l.053.224a.75.75 0 0 1-.34 1.44l-1.71.405a8.965 8.965 0 0 1 1.69 5.378l1.71.405a.75.75 0 0 1 .34 1.44l-.224.053a.75.75 0 0 1-1.44-.34l-.405-1.71a8.965 8.965 0 0 1-5.378 1.69l-.405 1.71a.75.75 0 0 1-1.44.34l-.053-.224a.75.75 0 0 1 .34-1.44l.405-1.71a8.966 8.966 0 0 1-5.378-1.69l-1.71-.405a.75.75 0 0 1-.34-1.44l.224-.053a.75.75 0 0 1 1.44.34l1.71.405A8.966 8.966 0 0 1 2.625 12c0-1.99.63-3.843 1.69-5.378L2.605 6.217a.75.75 0 0 1-.34-1.44l.224-.053a.75.75 0 0 1 1.44.34L5.64 5.472A8.966 8.966 0 0 1 9.458 1.412ZM12 8.25a3.75 3.75 0 1 0 0 7.5 3.75 3.75 0 0 0 0-7.5Z" clip-rule="evenodd" /></svg>
              <span>{{ $t('nav.settings') }}</span>
            </router-link>
          </li>
          <li>
            <router-link
              to="/dashboard/plan"
              :class="{ active: $route.path.startsWith('/dashboard/plan') }"
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M11.7 2.3a1 1 0 0 1 0-1.4l.01-.01a1 1 0 0 1 1.41 0l2.3 2.29a1 1 0 0 1 0 1.42L13.12 7.9a1 1 0 0 1-1.42 0l-.01-.01a1 1 0 0 1 0-1.41L12.3 4H8a4 4 0 0 0-4 4v3a1 1 0 1 1-2 0V8a6 6 0 0 1 6-6h4.3l-1.6-1.7Zm8 9.4a1 1 0 0 1 0 1.4l-.01.01a1 1 0 0 1-1.41 0l-2.3-2.29a1 1 0 0 1 0-1.42l2.3-2.29a1 1 0 0 1 1.42 0l.01.01a1 1 0 0 1 0 1.41L19.7 11H20a4 4 0 0 1 4 4v3a1 1 0 1 1-2 0v-3a2 2 0 0 0-2-2h-.3l1.3 1.3a1 1 0 0 1 0 1.4l-.01.01a1 1 0 0 1-1.41 0l-2.3-2.29a1 1 0 0 1 0-1.42l2.3-2.29a1 1 0 0 1 1.42 0l.01.01a1 1 0 0 1 0 1.41L19.7 13H20a4 4 0 0 1 4 4v3a1 1 0 1 1-2 0v-3a2 2 0 0 0-2-2h-.3l1.3 1.3ZM8 13a1 1 0 0 1 1 1v2h2a1 1 0 1 1 0 2H9v2a1 1 0 1 1-2 0v-2H5a1 1 0 1 1 0-2h2v-2a1 1 0 0 1 1-1Z"/></svg>
              <span>Мой план</span>
            </router-link>
          </li>
        </ul>
      </nav>
      <div class="sidebar-footer">
        <button @click="requestLogout" class="logout-button">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path fill-rule="evenodd" d="M7.5 3.75A1.5 1.5 0 0 0 6 5.25v13.5a1.5 1.5 0 0 0 1.5 1.5h6a1.5 1.5 0 0 0 1.5-1.5V15a.75.75 0 0 1 1.5 0v3.75a3 3 0 0 1-3 3h-6a3 3 0 0 1-3-3V5.25a3 3 0 0 1 3-3h6a3 3 0 0 1 3 3V9A.75.75 0 0 1 15 9V5.25a1.5 1.5 0 0 0-1.5-1.5h-6Zm10.72 4.72a.75.75 0 0 1 1.06 0l3 3a.75.75 0 0 1 0 1.06l-3 3a.75.75 0 1 1-1.06-1.06l1.72-1.72H9a.75.75 0 0 1 0-1.5h10.94l-1.72-1.72a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" /></svg>
          <span>{{ $t('nav.logout') }}</span>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <div v-if="showTrialBanner" class="trial-banner" :class="{ 'trial-ending-soon': (daysLeft||0) <= 3 }">
        <div class="trial-text">
          <strong>Trial</strong> — осталось {{ daysLeft }} {{ dayWord }}. План: TRIAL.
          <span v-if="daysLeft === 0">Срок истёк — обновите план, чтобы продолжить без ограничений.</span>
        </div>
        <div class="trial-actions">
          <button class="upgrade-btn" @click="goUpgrade">Перейти на Starter</button>
          <button class="close-btn" @click="dismissTrial">×</button>
        </div>
      </div>
      <div class="topbar">
        <div class="topbar-spacer"></div>
        <div class="topbar-actions">
          <LangSwitcher />
        </div>
      </div>
      <router-view />
    </main>

    <!-- Logout confirm modal -->
    <div v-if="showLogoutConfirm" class="modal-overlay" @keydown.esc.prevent="cancelLogout" tabindex="-1">
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="logout-title">
        <p id="logout-title">{{ $t('modal.logout.title') }}</p>
        <div class="modal-actions">
          <button class="modal-btn danger" @click="confirmLogout">{{ $t('modal.logout.confirm') }}</button>
          <button class="modal-btn secondary" @click="cancelLogout">{{ $t('modal.logout.cancel') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from '@/axios-setup';
import LangSwitcher from '@/components/LangSwitcher.vue';
import { billingUsageState, loadBillingUsage } from '@/billing/usageStore.js';

export default {
  name: 'DashboardLayout',
  components: { LangSwitcher },
  data() {
    return {
      username: '',
      email: '',
      firstName: '',
      lastName: '',
      companyName: '',
      role: 'MANAGER',
      showLogoutConfirm: false,
      profileUpdatedHandler: null,
      companyUpdatedHandler: null,
      unreadCount: 0,
      notifInterval: null,
      trialDismissed: false,
    };
  },
  computed: {
    displayName() {
      if (this.companyName) return this.companyName;
      const full = `${this.firstName || ''} ${this.lastName || ''}`.trim();
      if (full) return full;
      return this.username || this.email || '';
    },
    userInitials() {
      const full = `${this.firstName || ''} ${this.lastName || ''}`.trim();
      if (full) return full.charAt(0).toUpperCase();
      const base = this.companyName || this.username || this.email || '';
      return base ? base.charAt(0).toUpperCase() : '';
    },
    isTrial() {
      return billingUsageState.isTrial;
    },
    daysLeft() {
      return billingUsageState.daysLeft;
    },
    showTrialBanner() {
      if (this.trialDismissed) return false;
      if (!this.isTrial) return false;
      if (this.daysLeft == null) return false;
      return true;
    },
    dayWord() {
      const d = this.daysLeft;
      if (d === 1) return 'день';
      if (d >= 2 && d <= 4) return 'дня';
      return 'дней';
    }
  },
  methods: {
    changeLang(locale) {
      try {
        this.$i18n.locale = locale;
        localStorage.setItem('locale', locale);
        document.documentElement.setAttribute('lang', locale);
      } catch (e) {
        // ignore localization switch errors
        void 0;
      }
    },
    requestLogout(){
      this.showLogoutConfirm = true;
    },
    confirmLogout(){
      this.showLogoutConfirm = false;
      this.logout();
    },
    cancelLogout(){
      this.showLogoutConfirm = false;
    },
    logout() {
      localStorage.removeItem('user-token');
      localStorage.removeItem('user-id');
      try { localStorage.removeItem('user-role'); } catch (e) { void 0; }
      this.$router.push('/');
    },
    async fetchUnread() {
      try {
        const token = localStorage.getItem('user-token');
        if (!token) return;
        const res = await axios.get('http://127.0.0.1:8000/api/notifications/unread-count/', { headers: { Authorization: `Token ${token}` }});
        this.unreadCount = res.data.unread || 0;
      } catch (e) { /* silent */ }
    },
    async ensureBillingUsage() {
      try { await loadBillingUsage(); } catch (e) { /* ignore */ }
    },
    dismissTrial() {
      this.trialDismissed = true;
      try { sessionStorage.setItem('trial-banner-dismissed', '1'); } catch (e) { /* ignore */ }
    },
    goUpgrade() {
      // Пока просто уведомление. Позже — переход на страницу оплаты.
      this.$toast && this.$toast.info('Функция апгрейда скоро будет доступна.');
    }
  },
  async created() {
    const token = localStorage.getItem('user-token');
    if (!token) {
      this.$router.push('/login');
      return;
    }
    try {
      const response = await axios.get('/api/user-info/', { headers: { Authorization: `Token ${token}` } });
      this.username = response.data.username;
      this.email = response.data.email;
      this.firstName = response.data.first_name || '';
      this.lastName = response.data.last_name || '';
      this.role = (response.data.role || 'MANAGER').toUpperCase();
      try { localStorage.setItem('user-role', this.role); } catch (e) { void 0; }
      // Load company name for sidebar display
      try {
        const cs = await axios.get('/api/company/settings/', { headers: { Authorization: `Token ${token}` } });
        this.companyName = (cs.data && cs.data.name) || '';
      } catch (e) { /* ignore */ }
    } catch (error) {
      console.error('Ошибка получения данных пользователя:', error);
      localStorage.removeItem('user-token');
      this.$router.push('/login');
    }

    this.profileUpdatedHandler = (e) => {
      const d = (e && e.detail) || {};
      if (typeof d.username === 'string') this.username = d.username;
      if (typeof d.first_name === 'string') this.firstName = d.first_name;
      if (typeof d.last_name === 'string') this.lastName = d.last_name;
    };
    window.addEventListener('user-profile-updated', this.profileUpdatedHandler);
    this.companyUpdatedHandler = (e) => {
      const d = (e && e.detail) || {};
      if (typeof d.name === 'string') this.companyName = d.name;
    };
    window.addEventListener('company-updated', this.companyUpdatedHandler);
    // Старт обновления уведомлений
    this.fetchUnread();
    this.notifInterval = setInterval(this.fetchUnread, 30000); // каждые 30 секунд
    window.addEventListener('notifications-updated', this.fetchUnread);
    try { if (sessionStorage.getItem('trial-banner-dismissed') === '1') this.trialDismissed = true; } catch (e) { /* ignore */ }
    this.ensureBillingUsage();
  },
  beforeUnmount() {
    if (this.profileUpdatedHandler) {
      window.removeEventListener('user-profile-updated', this.profileUpdatedHandler);
    }
    if (this.companyUpdatedHandler) {
      window.removeEventListener('company-updated', this.companyUpdatedHandler);
    }
    window.removeEventListener('notifications-updated', this.fetchUnread);
    if (this.notifInterval) clearInterval(this.notifInterval);
  }
};
</script>

<style>
/* Глобальные CSS‑переменные — НЕ scoped, чтобы применялись повсюду */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  /* Светлая тема по умолчанию */
  --primary-color: #4A90E2;
  --dark-blue: #2c3e50;
  --sidebar-bg: #ffffff;            /* белая боковая панель */
  --sidebar-text: #4b5563;          /* серый текст */
  --sidebar-title: #111827;         /* цвет логотипа/заголовков в сайдбаре */
  --sidebar-card-bg: rgba(0,0,0,0.04);
  --sidebar-text-hover: #ffffff;    /* цвет текста на активном синем фоне */
  --background-color: #f7f9fc;      /* фон контента */
}

/* Тёмная тема */
[data-theme="dark"] {
  --primary-color: #4A90E2;
  --dark-blue: #2c3e50;
  --sidebar-bg: #111827;            /* тёмная боковая панель */
  --sidebar-text: #a0aec0;          /* светлый текст */
  --sidebar-title: #ffffff;         /* логотип в сайдбаре */
  --sidebar-card-bg: rgba(255,255,255,0.06);
  --sidebar-text-hover: #ffffff;    /* текст на активном синем фоне */
  --background-color: #0f172a;      /* тёмный фон контента */
}
</style>

<style scoped>

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  font-family: 'Inter', sans-serif;
}

.trial-banner {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(90deg,#2563eb,#1d4ed8);
  color: #fff;
  padding: 14px 18px;
  border-radius: 10px;
  margin: 12px 18px 0 18px;
  box-shadow: 0 4px 14px rgba(0,0,0,0.15);
  font-size: 14px;
  gap: 16px;
}
.trial-banner.trial-ending-soon {
  background: linear-gradient(90deg,#dc2626,#b91c1c);
}
.trial-banner .trial-text strong {
  font-weight: 600;
  margin-right: 6px;
}
.trial-actions {
  display: flex;
  gap: 8px;
}
.upgrade-btn {
  background: #fbbf24;
  color: #1f2937;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.25);
  transition: background .2s;
}
.upgrade-btn:hover { background: #f59e0b; }
.close-btn {
  background: rgba(255,255,255,0.18);
  border: none;
  color: #fff;
  width: 32px; height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  display: flex; align-items: center; justify-content: center;
  transition: background .2s;
}
.close-btn:hover { background: rgba(255,255,255,0.3); }

.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 260px;
  background-color: var(--sidebar-bg);
  color: var(--sidebar-text);
  display: flex;
  flex-direction: column;
  padding: 20px;
  z-index: 1000;
  transition: transform 0.3s ease;
  box-sizing: border-box; /* Добавим и сюда для надежности */
}

.sidebar-header {
  margin-bottom: 30px;
}

.logo {
  font-size: 24px;
  font-weight: 700;
  text-decoration: none;
  color: var(--sidebar-title);
}

.user-profile {
  display: flex;
  align-items: center;
  margin-bottom: 40px;
  padding: 10px;
  background-color: var(--sidebar-card-bg);
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
  color: var(--sidebar-title);
  white-space: normal;
  overflow: hidden;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  word-break: break-word;
  max-width: 170px;
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
  white-space: nowrap;
  position: relative;
}

.nav-links a svg {
  width: 20px;
  height: 20px;
  margin-right: 15px;
  flex-shrink: 0;
}
.notif-label { display: inline-flex; align-items: center; gap: 6px; }
.badge { background: #ef4444; color: #fff; padding: 0 6px; border-radius: 10px; font-size: 11px; line-height: 18px; font-weight: 600; min-width: 20px; text-align: center; }

 .nav-links a:hover, .nav-links a.router-link-exact-active, .nav-links a.active {
  background-color: var(--primary-color);
  color: var(--sidebar-text-hover);
}

/* Индикатор активного пункта слева */
.nav-links a.active::before,
.nav-links a.router-link-exact-active::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 22px;
  background-color: var(--sidebar-text-hover);
  border-radius: 2px;
}

.sidebar-footer {
  margin-top: auto;
}

.logout-button {
  width: 100%;
  padding: 12px;
  background: rgba(255,82,82,0.12);
  border: 1px solid rgba(255,82,82,0.45);
  color: #c53030;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-sizing: border-box; /* <-- ВОТ ИСПРАВЛЕНИЕ */
}

.logout-button svg {
  width: 20px;
  height: 20px;
  margin-right: 10px;
  flex-shrink: 0;
}

.logout-button:hover {
  background: rgba(255,82,82,0.18);
  color: #a61b1b;
  border-color: rgba(255,82,82,0.6);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.modal {
  background: #fff;
  padding: 24px 28px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.25);
  max-width: 420px;
  width: 92vw;
}
.modal p {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--dark-blue);
  font-weight: 500;
}
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; }
.modal-btn {
  padding: 10px 18px;
  border-radius: 10px;
  border: 1px solid transparent;
  cursor: pointer;
  font-weight: 600;
}
.modal-btn.primary { background: var(--primary-color); color: #fff; }
.modal-btn.secondary { background: #f0f2f5; color: var(--dark-blue); }
/* Danger variant for logout / destructive confirms */
.modal-btn.danger {
  background: rgba(255,82,82,0.12);
  border: 1px solid rgba(255,82,82,0.45);
  color: #c53030;
}
.modal-btn.danger:hover {
  background: rgba(255,82,82,0.20);
  border-color: rgba(255,82,82,0.6);
  color: #a61b1b;
}

.main-content {
  flex-grow: 1;
  background-color: var(--background-color);
  margin-left: 260px;
  width: calc(100% - 260px);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 900; /* under any modals */
  background: var(--background-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  /* reduce overall height a bit */
  padding: 12px 24px 0 24px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar-toggle {
  display: none;
  position: fixed;
  top: 15px;
  left: 15px;
  z-index: 1001;
  background-color: var(--sidebar-bg);
  color: white;
  border: 1px solid var(--sidebar-text);
  border-radius: 8px;
  width: 40px;
  height: 40px;
  cursor: pointer;
}

.sidebar-footer { display: flex; flex-direction: column; gap: 12px; }

@media (max-width: 992px) {
  .sidebar {
    transform: translateX(-100%);
  }
  .sidebar.is-open {
    transform: translateX(0);
  }
  .sidebar-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .main-content {
    margin-left: 0;
    width: 100%;
    padding-left: 60px;
  }
}

/* Normalize top spacing of pages under the sticky topbar across all sections */
.main-content :deep(.content-wrapper),
.main-content :deep(.list-view-wrapper),
.main-content :deep(.page),
.main-content :deep(.calendar-page),
.main-content :deep(.finance-page),
.main-content :deep(.cases-page),
.main-content :deep(.client-dashboard) {
  /* avoid double stacking space from page wrappers */
  padding-top: 16px !important;
}
</style>