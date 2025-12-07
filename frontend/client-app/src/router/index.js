// файл: frontend/client-app/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'

// --- Страницы, которые не требуют бокового меню ---
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import VerifyEmailView from '../views/VerifyEmailView.vue'
import PasswordResetView from '../views/PasswordResetView.vue'
import PasswordResetConfirmView from '../views/PasswordResetConfirmView.vue'
import PrivacyPolicy from '../views/PrivacyPolicy.vue'
import CookiesPolicy from '../views/CookiesPolicy.vue'
import TermsView from '../views/TermsView.vue'
import FaqView from '../views/FaqView.vue'

// --- Главный макет и страницы личного кабинета ---
import DashboardLayout from '../layouts/DashboardLayout.vue'
import DashboardHomeView from '../views/DashboardHomeView.vue'
import ClientListView from '../views/ClientListView.vue'
import ClientDetailView from '../views/ClientDetailView.vue'
import FinanceView from '../views/FinanceView.vue'
import CalendarView from '../views/CalendarView.vue'
import SettingsView from '../views/SettingsView.vue'
import TasksView from '../views/TasksView.vue'
import NotificationsView from '../views/NotificationsView.vue'
import MyPlanView from '../views/MyPlanView.vue'
import AdminDashboardView from '../views/AdminDashboardView.vue'
import { billingUsageState, loadBillingUsage } from '@/billing/usageStore.js'

const routes = [
  // --- Маршруты без бокового меню ---
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView
  },
  {
    path: '/verify-email',
    name: 'verify-email',
    component: VerifyEmailView
  },
  {
    path: '/password-reset',
    name: 'password-reset',
    component: PasswordResetView
  },
  {
    path: '/password-reset/confirm/:uid/:token',
    name: 'password-reset-confirm',
    component: PasswordResetConfirmView
  },
  {
    path: '/privacy-policy',
    name: 'privacy-policy',
    component: PrivacyPolicy
  },
  {
    path: '/cookies-policy',
    name: 'cookies-policy',
    component: CookiesPolicy
  },
  {
    path: '/terms',
    name: 'terms',
    component: TermsView
  },
  {
    path: '/faq',
    name: 'faq-public',
    component: FaqView
  },

  // --- Маршруты ВНУТРИ личного кабинета (с постоянным боковым меню) ---
  {
    path: '/dashboard', // Основной путь для всего личного кабинета
    component: DashboardLayout, // Этот компонент-обертка будет всегда на экране
    meta: { requiresAuth: true }, // Защищаем все вложенные маршруты
    children: [
      {
        path: '', // Пустой путь, теперь это /dashboard
        name: 'dashboard',
        component: DashboardHomeView
      },
      {
        path: 'notifications',
        name: 'notifications',
        component: NotificationsView
      },
      {
        path: 'clients', // Теперь это /dashboard/clients
        name: 'client-list',
        component: ClientListView
      },
      {
        path: 'clients/:id', // Теперь это /dashboard/clients/1
        name: 'client-detail',
        component: ClientDetailView,
        props: true
      },
      {
        path: 'finance', // /dashboard/finance
        name: 'finance',
        component: FinanceView
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: TasksView
      },
      {
        path: 'calendar',
        name: 'calendar',
        component: CalendarView
      },
      {
        path: 'settings',
        name: 'settings',
        component: SettingsView
      },
      {
        path: 'plan',
        name: 'my-plan',
        component: MyPlanView
      },
      {
        path: 'faq',
        name: 'faq',
        component: FaqView
      },
      {
        path: 'admin',
        name: 'admin-dashboard',
        component: AdminDashboardView,
        meta: { requiresSuperuser: true }
      },
      // Сюда вы будете добавлять новые маршруты: 'cases', 'tasks' и т.д.
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  // Глобально возвращаем страницу к началу при каждой навигации
  // (Vue Router v4 использует left/top; savedPosition восстанавливает историю браузера)
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { left: 0, top: 0 }
  }
})

// Навигационный гвард для проверки авторизации и ролей
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('user-token')
  const role = localStorage.getItem('user-role')
  const isSuperuser = localStorage.getItem('is-superuser') === '1'

  // Проверяем, требует ли маршрут (или его родитель) авторизации
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      // Если да, и токена нет - перенаправляем на страницу входа
      next('/login')
      return
    }

    // Если пользователь авторизован, проверим статус подписки
    try {
      await loadBillingUsage()
    } catch (e) {
      console.error('Failed to load billing usage', e)
    }

    // Check subscription management permission for plan page
    if (to.name === 'my-plan') {
      let perms = {}
      try {
        perms = JSON.parse(localStorage.getItem('user-permissions') || '{}')
      } catch (e) { /* ignore */ }
      if (!perms.can_manage_subscription) {
        next('/dashboard')
        return
      }
    }

    if (billingUsageState.isRestricted) {
      let perms = {}
      try {
        perms = JSON.parse(localStorage.getItem('user-permissions') || '{}')
      } catch (e) { /* ignore */ }
      const canManageSub = !!perms.can_manage_subscription
      const allowedNames = ['settings', 'faq']
      if (canManageSub) allowedNames.push('my-plan')
      if (!allowedNames.includes(to.name)) {
        window.dispatchEvent(new CustomEvent('show-restricted-toast'))
        // Redirect to plan only if user can manage subscription, otherwise to settings
        next({ name: canManageSub ? 'my-plan' : 'settings' })
        return
      }
    }
  }

  // Роут только для суперпользователя
  if (to.matched.some(r => r.meta && r.meta.requiresSuperuser) && !isSuperuser) {
    next('/dashboard')
    return
  }

  // Ассистентам запрещаем прямой доступ к разделу финансов
  if (to.path.startsWith('/dashboard/finance') && role === 'ASSISTANT') {
    next('/dashboard')
    return
  } else {
    // Иначе - разрешаем переход
    next()
  }
})

export default router