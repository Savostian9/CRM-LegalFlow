<template>
  <div class="finance-page">
    <header class="finance-header">
      <h1>{{ $t('finance.title') }}</h1>
      <div class="filters">
        <input v-model="search" type="text" :placeholder="$t('clients.searchPlaceholder')" />
        <UiSelect
          v-model="status"
          :options="[
            { value: 'all', label: $t('common.all') },
            { value: 'paid', label: 'Оплачено' },
            { value: 'debt', label: 'С задолженностью' }
          ]"
          :placeholder="$t('common.all')"
          aria-label="Status"
        />
      </div>
    </header>

    <section class="finance-stats" v-if="!loading">
      <div class="stat">
        <div class="label">{{ $t('finance.revenue') }}</div>
        <div class="value">{{ formatCurrency(totalPaid) }}</div>
      </div>
      <div class="stat">
        <div class="label">{{ $t('finance.plan') }}</div>
        <div class="value">{{ formatCurrency(totalCost) }}</div>
      </div>
      <div class="stat">
        <div class="label">{{ $t('finance.debt') }}</div>
        <div class="value debt">{{ formatCurrency(totalDebt) }}</div>
      </div>
    </section>

      <div v-if="!loading && role !== 'MANAGER'" class="manager-filter-bar below-stats">
        <label class="mf-label">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.33 0-8 2.17-8 5v1h16v-1c0-2.83-3.67-5-8-5Z" />
          </svg>
          {{ $t('clients.manager') }}
        </label>
        <UiSelect
          class="mf-select"
          v-model="managerFilter"
          :options="[{ value: '', label: ($t('clients.extra.allOption')||$t('common.all')) }, ...managerOptions.map(m => ({ value: String(m.id), label: m.name }))]"
          :placeholder="$t('clients.extra.allOption') || $t('common.all')"
          :aria-label="$t('clients.manager')"
        />
        <button class="mf-clear" v-if="managerFilter" @click="managerFilter=''">{{ $t('clients.extra.reset') || 'Reset' }}</button>
      </div>

    <div v-if="loading" class="loader">{{ $t('common.loading') }}</div>

    <table v-else class="finance-table">
      <colgroup>
        <col style="width: 26%" />
        <col style="width: 26%" />
        <col style="width: 12%" />
        <col style="width: 12%" />
        <col style="width: 12%" />
        <col style="width: 12%" />
      </colgroup>
      <thead>
        <tr>
          <th>{{ $t('finance.columns.name') }}</th>
          <th>{{ $t('finance.columns.email') }}</th>
          <th>{{ $t('finance.columns.manager') }}</th>
          <th class="right">{{ $t('finance.columns.cost') }}</th>
          <th class="right">{{ $t('finance.columns.paid') }}</th>
          <th class="right">{{ $t('finance.columns.balance') }}</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="c in filteredClients"
          :key="c.id"
          :class="{ debt: balance(c) > 0, paid: balance(c) <= 0, 'client-row': true }"
          @click="openClient(c.id)"
          role="button"
          tabindex="0"
          @keydown.enter="openClient(c.id)"
        >
          <td>{{ c.first_name }} {{ c.last_name }}</td>
          <td>{{ c.email }}</td>
          <td>{{ formatManagerName(c) }}</td>
          <td class="right">{{ formatCurrency(c.service_cost) }}</td>
          <td class="right">{{ formatCurrency(c.amount_paid) }}</td>
          <td class="right" :class="{ negative: balance(c) < 0 }">{{ formatCurrency(balance(c)) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import axios from 'axios';
import UiSelect from '../components/UiSelect.vue';

export default {
  name: 'FinanceView',
  components: { UiSelect },
  data() {
    return {
      loading: true,
      clients: [],
      search: '',
      status: 'all', // all | paid | debt
      role: 'MANAGER',
      managerFilter: '',
  /* manager dropdown UI removed in favor of standalone select */
      managers: [],
    };
  },
  computed: {
    managerOptions() {
      // Собираем всех пользователей компании (если загружены) + авторов клиентов
      const map = new Map();
      (this.managers || []).forEach(u => {
        if (u && u.id != null) map.set(String(u.id), this.userDisplayName(u));
      });
      (this.clients || []).forEach(c => {
        if (c && c.created_by_id != null) {
          const id = String(c.created_by_id);
          if (!map.has(id)) {
            const first = (c.created_by_first_name || '').trim();
            const last = (c.created_by_last_name || '').trim();
            const full = `${first} ${last}`.trim();
            const name = full || (c.created_by_name || `ID ${id}`);
            map.set(id, name);
          }
        }
      });
      return Array.from(map, ([id, name]) => ({ id, name }))
        .sort((a,b)=> String(a.name).localeCompare(String(b.name), 'ru'));
    },
    filteredClients() {
      const q = this.search.trim().toLowerCase();
      let list = this.clients;
      if (q) {
        list = list.filter(c => {
          const managerFull = `${c.created_by_first_name || ''} ${c.created_by_last_name || ''}`.trim();
          return `${c.first_name} ${c.last_name} ${c.email} ${managerFull} ${c.created_by_name || ''}`.toLowerCase().includes(q);
        });
      }
      if (this.status === 'paid') {
        list = list.filter(c => this.balance(c) <= 0);
      } else if (this.status === 'debt') {
        list = list.filter(c => this.balance(c) > 0);
      }
      if (this.managerFilter) {
        list = list.filter(c => {
          const id = c.created_by_id != null ? String(c.created_by_id) : null;
            return id === this.managerFilter;
        });
      }
      return list;
    },
    totalPaid() {
      return this.clients.reduce((s, c) => s + Number(c.amount_paid || 0), 0);
    },
    totalCost() {
      return this.clients.reduce((s, c) => s + Number(c.service_cost || 0), 0);
    },
    totalDebt() {
      return this.clients.reduce((s, c) => s + Math.max(0, this.balance(c)), 0);
    }
  },
  created() {
    try { this.role = String(localStorage.getItem('user-role') || 'MANAGER').toUpperCase(); } catch (e) { this.role = 'MANAGER'; }
    this.fetch();
    if (this.role !== 'MANAGER') this.loadManagers();
  },
  methods: {
    // Возвращает отображаемое имя менеджера по его id (строкой)
    managerNameById(id) {
      if (!id) return '-';
      const m = (this.managers || []).find(u => String(u.id) === String(id));
      if (m) return this.userDisplayName(m);
      // fallback: попытаться найти среди клиентов автора
      for (const c of this.clients || []) {
        if (String(c.created_by_id) === String(id)) {
          const first = (c.created_by_first_name || '').trim();
            const last = (c.created_by_last_name || '').trim();
            const full = `${first} ${last}`.trim();
            return full || c.created_by_name || `ID ${id}`;
        }
      }
      return `ID ${id}`;
    },
    async loadManagers() {
      const token = localStorage.getItem('user-token');
      if (!token) return;
      try {
        const resp = await axios.get('http://127.0.0.1:8000/api/company/users/', { headers: { Authorization: `Token ${token}` } });
        const users = Array.isArray(resp.data) ? resp.data : [];
        // Показываем всех (кроме, при желании, клиентов / внешних ролей). Уберём только чисто клиентские аккаунты если есть флаг is_client
        this.managers = users.filter(u => !u.is_client); // если нужно включить и клиентов, заменить на users
      } catch (e) {
        // Fallback: build from clients if no API permission
        this.managers = this.buildManagersFromClients();
      }
    },
    buildManagersFromClients(){
      const map = new Map();
      for (const c of this.clients || []){
        if (c.created_by_id){
          const name = (c.created_by_name || `${c.created_by_first_name || ''} ${c.created_by_last_name || ''}`.trim() || `ID ${c.created_by_id}`);
          map.set(String(c.created_by_id), name);
        }
      }
      return Array.from(map, ([id, name]) => ({ id, first_name: name, last_name: '', username: name }));
    },
    userDisplayName(u){
      const fn = (u.first_name || '').trim();
      const ln = (u.last_name || '').trim();
      const full = `${fn} ${ln}`.trim();
      return full || u.username || `User ${u.id}`;
    },
    setManagerFilter(val){ this.managerFilter = val; },
    async fetch() {
      const token = localStorage.getItem('user-token');
      if (!token) { this.$router.push('/login'); return; }
      this.loading = true;
      try {
        const resp = await axios.get('http://127.0.0.1:8000/api/clients/', { headers: { Authorization: `Token ${token}` } });
        this.clients = resp.data;
        // If we don't have managers loaded yet and role allows, build fallback list
        if (this.role !== 'MANAGER' && (!this.managers || this.managers.length === 0)) {
          this.managers = this.buildManagersFromClients();
        }
      } catch (e) {
        console.error('Ошибка загрузки клиентов', e);
      } finally {
        this.loading = false;
      }
    },
    balance(c) {
      return Number(c.service_cost || 0) - Number(c.amount_paid || 0);
    },
    formatCurrency(val) {
      const num = Number(val || 0);
      try {
        return num.toLocaleString('ru-RU', { style: 'currency', currency: 'PLN', minimumFractionDigits: 2 });
      } catch (e) {
        return `${num.toFixed(2)} PLN`;
      }
    },
    openClient(id) {
      this.$router.push({ path: `/dashboard/clients/${id}`, query: { from: 'finance' } });
    },
    formatManagerName(c) {
      const first = (c.created_by_first_name || '').trim();
      const last = (c.created_by_last_name || '').trim();
      const full = `${first} ${last}`.trim();
      return full || (c.created_by_name || '-')
    },
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.finance-page { padding: 40px; font-family: 'Inter', sans-serif; }
.finance-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
.finance-header h1 { font-size: 28px; color: #2c3e50; font-weight: 700; }

.filters { display: flex; gap: 10px; }
.filters input, .filters select { height: 40px; padding: 0 12px; border: 1px solid var(--form-border); border-radius: var(--form-radius,8px); font-family: 'Inter', sans-serif; transition:border-color .18s, box-shadow .18s; display:inline-flex; align-items:center; background:var(--form-bg,#fff); }
.filters :deep(.ui-select__trigger){ height:40px; padding:0 12px; border-radius:var(--form-radius,8px); display:inline-flex; align-items:center; }
.filters input:focus, .filters select:focus { outline:none; border-color:var(--form-border-focus); box-shadow:var(--form-focus-ring); }

/* Manager filter bar (second row) */
.manager-filter-bar { display:flex; align-items:center; gap:16px; margin-top:14px; background:#fff; border:1px solid #e0e6ed; border-radius:10px; padding:10px 18px; }
.manager-filter-bar .mf-label { display:inline-flex; align-items:center; gap:6px; font-size:13px; font-weight:600; color:#5a6a7b; }
.manager-filter-bar .mf-select { min-width:220px; }
.manager-filter-bar .mf-clear { background:none; border:none; color:#111827; font-size:12px; cursor:pointer; }
.manager-filter-bar .mf-clear:hover { text-decoration:underline; }

.finance-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 16px; }
.stat { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 10px; padding: 14px; }
.stat .label { color: #5a6a7b; font-size: 13px; margin-bottom: 4px; }
.stat .value { font-weight: 700; font-size: 18px; }
.stat .value.debt { color: #c0392b; }

.loader { padding: 20px; color: #5a6a7b; }

/* Table styles to match Clients page */
.finance-table { width: 100%; border-collapse: collapse; table-layout: fixed; background-color: var(--card-bg); border-radius: 12px; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.07); overflow: hidden; position: relative; z-index: 1; font-family: 'Inter', sans-serif; }
.finance-table th, .finance-table td { padding: 14px 16px; text-align: left; }
.finance-table thead th { background-color: #f7f9fc; font-size: 14px; color: #5a6a7b; font-weight:700; position: relative; }
.finance-table thead th.right { text-align: left; }
.finance-table thead th:nth-child(4),
.finance-table thead th:nth-child(5),
.finance-table thead th:nth-child(6) { text-align: left; }
.finance-table td { border-top: 1px solid #e0e6ed; font-size: 15px; white-space: nowrap; }
.finance-table tbody td:nth-child(4),
.finance-table tbody td:nth-child(5),
.finance-table tbody td:nth-child(6) {
  white-space: nowrap;
}
.finance-table td:nth-child(1),
.finance-table td:nth-child(2),
.finance-table td:nth-child(3) {
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 0; /* so colgroup widths govern and text truncates */
}

/* Zebra rows and hover like Clients */
.finance-table tbody tr.client-row:nth-child(even) { background-color: #f7f9fc; }
.client-row { cursor: pointer; transition: background-color 0.2s ease; }
.client-row:hover { background-color: #eef3f9; }

/* Numeric alignment */
.right { text-align: left; font-variant-numeric: tabular-nums; }
.finance-table td.right { font-size: 14px; }
.finance-table td:last-child, .finance-table thead th:last-child { text-align: left; }

/* Amount colors: Paid (col 5) green; Balance (col 6) red when there is debt */
.finance-table tbody td:nth-child(5) { color: #16a34a; font-weight: 700; }
.finance-table tbody tr.debt td:nth-child(6) { color: #d14343; font-weight: 700; }

/* Manager filter dropdown styles (scoped) */
/* (manager-filter wrapper removed; using plain UiSelect aligned with other filters) */
</style>
