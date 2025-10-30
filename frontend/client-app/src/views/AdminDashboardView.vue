<template>
  <div class="admin-page page">
    <h1>Админ-панель</h1>
    <div v-if="loading" class="loading">Загрузка…</div>
    <div v-else>
      <section class="cards">
        <div class="card"><div class="label">Компании</div><div class="value">{{ stats.totals.companies }}</div></div>
        <div class="card"><div class="label">Пользователи</div><div class="value">{{ stats.totals.users }}</div></div>
        <div class="card"><div class="label">Клиенты</div><div class="value">{{ stats.totals.clients }}</div></div>
        <div class="card"><div class="label">Дела</div><div class="value">{{ stats.totals.cases }}</div></div>
        <div class="card"><div class="label">Задачи</div><div class="value">{{ stats.totals.tasks }}</div></div>
        <div class="card"><div class="label">Напоминания</div><div class="value">{{ stats.totals.reminders }}</div></div>
      </section>

      <section class="plans">
        <h2>Планы</h2>
        <ul>
          <li v-for="p in stats.plans" :key="p.plan">{{ p.plan }} — {{ p.count }}</li>
        </ul>
      </section>

      <section class="companies">
        <h2>Компании</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Название</th>
                <th>План</th>
                <th>Пользователей</th>
                <th>Trial заканчивается</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in stats.companies" :key="c.id">
                <td>{{ c.id }}</td>
                <td>{{ c.name }}</td>
                <td>{{ c.plan }}</td>
                <td>{{ c.users_count }}</td>
                <td>{{ c.trial_ends_at ? new Date(c.trial_ends_at).toLocaleString() : '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="users">
        <h2>Пользователи</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Имя</th>
                <th>Email</th>
                <th>Роль</th>
                <th>Компания</th>
                <th>Последний вход</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in stats.users" :key="u.id">
                <td>{{ u.id }}</td>
                <td>{{ getUserName(u) }}</td>
                <td>{{ u.email }}</td>
                <td>{{ u.role }}</td>
                <td>
                  <span v-if="u.company_id">{{ u.company_name }} ({{ u.company_id }})</span>
                  <span v-else>-</span>
                </td>
                <td>{{ formatLastLogin(u.last_login) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import axios from '@/axios-setup'

export default {
  name: 'AdminDashboardView',
  data() {
    return {
      loading: true,
      stats: {
        totals: { companies: 0, users: 0, clients: 0, cases: 0, tasks: 0, reminders: 0 },
        plans: [],
        usersByRole: [],
        companies: [],
        users: []
      }
    }
  },
  async created() {
    const token = localStorage.getItem('user-token')
    try {
      const { data } = await axios.get('/api/admin/stats/', { headers: { Authorization: `Token ${token}` } })
      this.stats = data
    } catch (e) {
      this.$toast && this.$toast.error('Нет доступа или ошибка загрузки')
      this.$router.push('/dashboard')
      return
    } finally {
      this.loading = false
    }
  },
  methods: {
    getUserName(u) {
      const full = [u.first_name, u.last_name].filter(Boolean).join(' ')
      return full || u.username || `user#${u.id}`
    },
    formatLastLogin(dt) {
      if (!dt) return '—'
      try {
        return new Date(dt).toLocaleString()
      } catch (e) {
        return String(dt)
      }
    }
  }
}
</script>

<style scoped>
.admin-page { padding: 16px 24px; }
.loading { opacity: .7; }
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin: 12px 0 24px;
}
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.card .label { color: #6b7280; font-size: 12px; }
.card .value { font-size: 22px; font-weight: 700; color: #111827; }
.plans h2, .companies h2 { margin: 16px 0 8px; }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; }
th, td { padding: 10px 12px; border-bottom: 1px solid #f1f5f9; text-align: left; }
th { background: #f8fafc; font-weight: 600; font-size: 13px; color: #374151; }
tbody tr:hover { background: #f9fafb; }
</style>