// файл: frontend/client-app/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'

// --- Страницы, которые не требуют бокового меню ---
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import VerifyEmailView from '../views/VerifyEmailView.vue'
import PasswordResetView from '../views/PasswordResetView.vue'
import PasswordResetConfirmView from '../views/PasswordResetConfirmView.vue'

// --- Главный макет и страницы личного кабинета ---
import DashboardLayout from '../layouts/DashboardLayout.vue'
import DashboardHomeView from '../views/DashboardHomeView.vue'
import ClientListView from '../views/ClientListView.vue'
import ClientDetailView from '../views/ClientDetailView.vue'

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
      // Сюда вы будете добавлять новые маршруты: 'cases', 'tasks' и т.д.
    ]
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// Навигационный гвард для проверки авторизации
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('user-token')

  // Проверяем, требует ли маршрут (или его родитель) авторизации
  if (to.matched.some(record => record.meta.requiresAuth) && !token) {
    // Если да, и токена нет - перенаправляем на страницу входа
    next('/login')
  } else {
    // Иначе - разрешаем переход
    next()
  }
})

export default router