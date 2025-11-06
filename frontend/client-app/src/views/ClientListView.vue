<template>
  <div class="list-view-wrapper">
    <header class="content-header">
      <h1>{{ $t('clients.title') }}</h1>
      <!-- Кнопка не видна ассистенту; клиентам показываем только если у них ещё нет профиля -->
      <button 
        v-if="canAddClient()" 
        @click="showAddClientModal = true" 
        class="btn"
      >{{ $t('clients.add') }}</button>
    </header>

    <div class="search-section">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          :placeholder="$t('clients.searchPlaceholder')" 
          class="search-input"
        >
        <span class="search-icon" aria-hidden="true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-4.35-4.35M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16z" />
          </svg>
        </span>
      </div>
      <div class="date-filter modern">
        <div class="chips">
          <button :class="['chip', { active: preset === 'all' }]" @click="setPreset('all')">{{ $t('clients.date.all') }}</button>
          <button :class="['chip', { active: preset === 'today' }]" @click="setPreset('today')">{{ $t('clients.date.today') }}</button>
          <button :class="['chip', { active: preset === '7d' }]" @click="setPreset('7d')">{{ $t('clients.date.seven') }}</button>
          <button :class="['chip', { active: preset === 'month' }]" @click="setPreset('month')">{{ $t('clients.date.month') }}</button>
          <button :class="['chip', { active: preset === 'custom' }]" @click="toggleCustomRange">{{ $t('clients.date.custom') }}</button>
        </div>
        <div v-if="showCustomDate" class="custom-range">
          <label class="date-label">
            {{ $t('clients.extra.from') }}
            <AltDateTimePicker mode="date" v-model="createdFrom" @change="reloadClients" />
          </label>
          <label class="date-label">
            {{ $t('clients.extra.to') }}
            <AltDateTimePicker mode="date" v-model="createdTo" @change="reloadClients" />
          </label>
          <button class="clear-chip" v-if="createdFrom || createdTo" @click="clearCustomRange">{{ $t('clients.extra.reset') }}</button>
        </div>

        <div class="creator-filter" v-if="isAdminRole">
          <label class="creator-label">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
              <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5Zm0 2c-4.33 0-8 2.17-8 5v1h16v-1c0-2.83-3.67-5-8-5Z"/>
            </svg>
            {{ $t('clients.manager') }}
          </label>
          <UiSelect
            v-model="creatorFilter"
            :options="[{ value: '', label: $t('clients.extra.allOption') }, ...creatorOptions.map(c => ({ value: String(c.id), label: c.name }))]"
            :placeholder="$t('clients.extra.allOption')"
            :aria-label="$t('clients.manager')"
          />
          <button class="clear-chip creator-clear" v-if="creatorFilter" @click="creatorFilter=''; reloadClients();">{{ $t('clients.extra.reset') }}</button>
        </div>
      </div>
    </div>

    <div class="content-body">
      <div v-if="loading" class="loader">{{ $t('common.loading') }}</div>
      
      <div v-if="!loading && clients.length === 0" class="empty-state">
        <p>{{ $t('clients.extra.empty') }}</p>
      </div>
      
      <table v-if="!loading && clients.length > 0" class="clients-table">
        <thead>
          <tr>
            <th>{{ $t('clients.columns.name') }}</th>
            <th>{{ $t('clients.columns.email') }}</th>
            <th>{{ $t('clients.columns.phone') }}</th>
            <th>{{ $t('clients.columns.manager') }}</th>
            <th class="sortable" @click="toggleSort" :aria-sort="sort === '-created_at' ? 'descending' : 'ascending'">
              <span class="sortable-label">{{ $t('clients.columns.created') }}</span>
              <span class="sort-icon" :class="{ desc: sort === '-created_at', asc: sort === 'created_at' }" aria-hidden="true">
                <svg v-if="sort === '-created_at'" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M7 10l5 5 5-5H7z"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M7 14l5-5 5 5H7z"/></svg>
              </span>
            </th>
            <th>
              <div class="status-header">
                <span>{{ $t('clients.columns.status') }}</span>
                <div class="filter-dropdown">
                  <button ref="statusFilterButton" class="filter-button" :class="{ active: !!statusFilter }" @click.stop="toggleStatusFilter" :aria-label="$t('clients.extra.statusFilterAria')" :title="$t('clients.extra.statusFilterAria')">
                    <!-- Фильтр (воронка) -->
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                      <path d="M3 5c0-1.1.9-2 2-2h14a2 2 0 0 1 1.6 3.2l-6.4 8.53V19a1 1 0 0 1-.55.89l-4 2A1 1 0 0 1 8 21v-6.27L1.4 6.2A2 2 0 0 1 3 5Zm2-1a1 1 0 0 0-.8 1.6l6.6 8.8a1 1 0 0 1 .2.6v4.58l2-1V15a1 1 0 0 1 .2-.6l6.6-8.8A1 1 0 0 0 19 4H5Z"/>
                    </svg>
                  </button>
                </div>
                <teleport to="body">
                  <div 
                    v-if="showStatusFilter" 
                    class="filter-dropdown-content status-filter-dropdown" 
                    :style="{ top: dropdownPosition.top + 'px', left: dropdownPosition.left + 'px', minWidth: dropdownPosition.width + 'px' }"
                    @click.stop
                  >
                    <div 
                      class="filter-option"
                      :class="{ active: statusFilter === '' }"
                      @click.stop="setStatusFilter('')"
                    >
                      <span class="status-indicator all-status"></span>
                      {{ $t('clients.extra.allStatuses') }}
                    </div>
                    <div 
                      v-for="status in statusOptions" 
                      :key="status.value"
                      class="filter-option"
                      :class="{ active: statusFilter === status.value }"
                      @click.stop="setStatusFilter(status.value)"
                    >
                      <span class="status-indicator" :class="`status-${status.value}`"></span>
                      {{ status.label }}
                    </div>
                  </div>
                </teleport>
              </div>
              <!-- Показываем активный фильтр -->
              <div v-if="statusFilter" class="active-filter">
                {{ $t('clients.extra.activeFilter') }} {{ getStatusLabelByValue(statusFilter) }}
                <button @click.stop="clearStatusFilter" class="clear-filter">×</button>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredClients.length === 0" class="no-results-row">
            <td colspan="6" class="no-results">{{ $t('clients.extra.noResults') }}</td>
          </tr>
          <tr v-for="client in filteredClients" :key="client.id" class="client-row" @click="openClient(client.id)">
            <td>{{ client.first_name }} {{ client.last_name }}</td>
            <td>{{ client.email }}</td>
            <td>{{ client.phone_number }}</td>
            <td>{{ formatManagerName(client) }}</td>
            <td>{{ formatDate(client.created_at) }}</td>
            <td>
              <span class="status-badge" :class="normalizeStatusClass(client.active_case_status_class)">
                {{ getStatusLabel(client.active_case_status_class) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Закрытие списка обрабатывается глобальным обработчиком клика -->
  </div>

  <AddClientModal 
    v-if="showAddClientModal" 
    :canChooseManager="canChooseManager()"
    :managers="managerOptions"
    @close="showAddClientModal = false" 
    @save="addNewClient"
  />
</template>

<script>
import axios from 'axios';
import AddClientModal from '@/components/AddClientModal.vue';
import UiSelect from '@/components/UiSelect.vue';

export default {
  name: 'ClientListView',
  components: {
    AddClientModal,
    UiSelect
  },
  data() {
    return {
    clients: [],
    loading: true,
    currentUser: { is_client: false, is_manager: false, email: '', role: 'MANAGER' },
      showAddClientModal: false,
      searchQuery: '',
      createdFrom: '',
      createdTo: '',
      sort: '-created_at',
      preset: 'all',
      showCustomDate: false,
      statusFilter: '',
      creatorFilter: '',
      showStatusFilter: false,
      dropdownPosition: { top: 0, left: 0, width: 220 },
      creatorOptions: [],
      managerOptions: []
    };
  },
  computed: {
    statusOptions() {
      return [
        { value: 'preparation', label: this.$t('case.status.preparation') },
        { value: 'submitted', label: this.$t('case.status.submitted') },
        { value: 'in_progress', label: this.$t('case.status.inProgress') },
        { value: 'decision_positive', label: this.$t('case.status.decisionPositive') },
        { value: 'decision_negative', label: this.$t('case.status.decisionNegative') },
        { value: 'closed', label: this.$t('case.status.closed') },
        { value: 'no-case', label: this.$t('case.status.none') }
      ];
    },
    isAdminRole(){
      return String(this.currentUser.role || '').toUpperCase() === 'ADMIN';
    },
    statusLabelMap() {

      return {
        'preparation': this.$t('case.status.preparation'),
        'submitted': this.$t('case.status.submitted'),
        'in_progress': this.$t('case.status.inProgress'),
        'decision_positive': this.$t('case.status.decisionPositive'),
        'decision_negative': this.$t('case.status.decisionNegative'),
        'closed': this.$t('case.status.closed'),
        'no-case': this.$t('case.status.none')
      };
    },
  filteredClients() {
      let filtered = this.clients;

      // Поиск по всем параметрам
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase().trim();
        filtered = filtered.filter(client => {
          const fullName = `${client.first_name || ''} ${client.last_name || ''}`.toLowerCase();
          const managerFull = `${client.created_by_first_name || ''} ${client.created_by_last_name || ''}`.toLowerCase();
          const managerName = (client.created_by_name || '').toLowerCase();
          return fullName.includes(query) ||
                 (client.email && client.email.toLowerCase().includes(query)) ||
                 (client.phone_number && client.phone_number.includes(query)) ||
                 managerFull.includes(query) || managerName.includes(query);
        });
      }

      // Фильтр по статусу
      if (this.statusFilter) {
        console.log('Фильтруем по статусу:', this.statusFilter); // Для отладки
        filtered = filtered.filter(client => {
          // Получаем значение статуса из класса
          const statusClass = client.active_case_status_class;
          console.log('Клиент:', client.first_name, 'Статус класса:', statusClass); // Для отладки
          
          if (!statusClass) {
            // Если у клиента нет статуса, проверяем фильтр "нет дела"
            return this.statusFilter === 'no-case';
          }
          
          // Извлекаем название статуса из класса (убираем 'status-')
          const statusValue = statusClass.replace('status-', '');
          console.log('Извлеченный статус:', statusValue); // Для отладки
          
          return statusValue === this.statusFilter;
        });
      }

      console.log('Отфильтровано клиентов:', filtered.length); // Для отладки
      return filtered;
    }
  },
  async created() {
    const token = localStorage.getItem('user-token');
    if (!token) {
      this.$router.push('/login');
      return;
    }

    try {
      // Сначала получим информацию о пользователе (роли)
      const me = await axios.get('http://127.0.0.1:8000/api/user-info/', {
        headers: { Authorization: `Token ${token}` }
      });
      this.currentUser = {
        is_client: !!me.data?.is_client,
        is_manager: !!me.data?.is_manager,
        email: me.data?.email || '',
        role: (me.data?.role || 'MANAGER')
      };

      // Подтянем список всех пользователей компании для фильтра (только если админ)
      if (this.isAdminRole) {
        await this.fetchCreators();
      } else {
        this.creatorOptions = [];
        this.creatorFilter = '';
      }

      // восстановим последний пресет из localStorage (необязательно)
      const savedPreset = localStorage.getItem('clientListPreset');
      if (savedPreset) {
        this.setPreset(savedPreset);
      } else {
        await this.reloadClients();
      }
      console.log('Загружены клиенты:', this.clients); // Для отладки
    } catch (error) {
      console.error("Ошибка при загрузке списка клиентов:", error);
    } finally {
      this.loading = false;
    }
  },
  methods: {
    canAddClient(){
      const role = String(this.currentUser.role || '').toUpperCase();
      if (role === 'ASSISTANT') return false;
      // если это клиент – позволим один раз создать свой профиль
      if (this.currentUser.is_client) {
        return this.clients.length === 0;
      }
      return true;
    },
    setPreset(p) {
      this.preset = p;
      try { localStorage.setItem('clientListPreset', p); } catch (e) { console.debug('Preset save skipped:', e?.message || e); }
      const today = new Date();
      const toLocalISODate = (d) => {
        const y = d.getFullYear();
        const m = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        return `${y}-${m}-${day}`;
      };
      if (p === 'all') {
        this.createdFrom = '';
        this.createdTo = '';
        this.showCustomDate = false;
      } else if (p === 'today') {
        const start = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        const end = new Date(today.getFullYear(), today.getMonth(), today.getDate());
        this.createdFrom = toLocalISODate(start);
        this.createdTo = toLocalISODate(end);
        this.showCustomDate = false;
      } else if (p === '7d') {
        const start = new Date(today);
        start.setDate(start.getDate() - 6);
        this.createdFrom = toLocalISODate(start);
        this.createdTo = toLocalISODate(today);
        this.showCustomDate = false;
      } else if (p === 'month') {
        const start = new Date(today.getFullYear(), today.getMonth(), 1);
        const end = new Date(today.getFullYear(), today.getMonth() + 1, 0);
        this.createdFrom = toLocalISODate(start);
        this.createdTo = toLocalISODate(end);
        this.showCustomDate = false;
      } else if (p === 'custom') {
        this.showCustomDate = true;
      }
      this.reloadClients();
    },
    toggleCustomRange(){
      if (this.preset !== 'custom') {
        this.preset = 'custom';
      }
      this.showCustomDate = !this.showCustomDate;
    },
    clearCustomRange(){
      this.createdFrom = '';
      this.createdTo = '';
      this.preset = 'all';
      this.showCustomDate = false;
      this.reloadClients();
    },
    async reloadClients(){
      const token = localStorage.getItem('user-token');
      const params = new URLSearchParams();
      if (this.createdFrom) params.append('created_from', this.createdFrom);
      if (this.createdTo) params.append('created_to', this.createdTo);
      if (this.sort) params.append('sort', this.sort);
      if (this.creatorFilter) params.append('created_by', this.creatorFilter);
      const url = `http://127.0.0.1:8000/api/clients/?${params.toString()}`;
      try{
        const response = await axios.get(url, { headers: { Authorization: `Token ${token}` } });
        this.clients = response.data;
        // Fallback: если не удалось загрузить список создателей от API компании (или он пуст), соберём из клиентов
        if (!this.creatorOptions.length) {
          const map = new Map();
          for (const cl of this.clients) {
            if (cl.created_by_id && cl.created_by_name) map.set(cl.created_by_id, cl.created_by_name);
          }
          this.creatorOptions = Array.from(map, ([id, name]) => ({ id, name })).sort((a,b)=> String(a.name).localeCompare(String(b.name), 'ru'));
        }
      } catch (e){
        console.error('Ошибка при загрузке списка клиентов:', e);
      }
    },
    async fetchCreators() {
      const token = localStorage.getItem('user-token');
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/company/users/', { headers: { Authorization: `Token ${token}` } });
        const users = Array.isArray(res.data) ? res.data : [];
        const toName = (u) => {
          const full = `${u.first_name || ''} ${u.last_name || ''}`.trim();
          if (full) return full;
          const uname = u.username || '';
          if (uname && !String(uname).includes('@')) return uname;
          return u.email || uname;
        };
        this.creatorOptions = users
          .map(u => ({ id: u.id, name: toName(u) }))
          .sort((a,b)=> String(a.name).localeCompare(String(b.name), 'ru'));
        // Также сохраним список менеджеров/руководителей для выбора в модалке
        this.managerOptions = users
          .filter(u => ['MANAGER','LEAD'].includes(String(u.role || '').toUpperCase()))
          .map(u => ({ id: u.id, name: toName(u), role: String(u.role || '').toUpperCase() }))
          .sort((a,b)=> String(a.name).localeCompare(String(b.name), 'ru'));
      } catch (err) {
        // Если нет прав (403) или иные проблемы — просто используем fallback из списка клиентов
        console.warn('Не удалось загрузить список пользователей компании:', err?.response?.status || err?.message || err);
        this.creatorOptions = [];
        this.managerOptions = [];
      }
    },
    toggleSort(){
      this.sort = this.sort === '-created_at' ? 'created_at' : '-created_at';
      this.reloadClients();
    },
    formatDate(dt) {
      if (!dt) return '-';
      try {
        const loc = (this.$i18n && this.$i18n.locale) || 'ru';
        const map = { ru: 'ru-RU', pl: 'pl-PL' };
        const d = new Date(dt);
        return d.toLocaleDateString(map[loc] || 'ru-RU');
      } catch { return '-'; }
    },
    toggleStatusFilter() {
      this.showStatusFilter = !this.showStatusFilter;
      if (this.showStatusFilter) {
        this.$nextTick(() => this.updateDropdownPosition());
      }
    },
    updateDropdownPosition() {
      const btn = this.$refs.statusFilterButton;
      if (!btn) return;
      const rect = btn.getBoundingClientRect();
      const scrollY = window.scrollY || window.pageYOffset;
      const scrollX = window.scrollX || window.pageXOffset;
      const top = rect.bottom + scrollY + 8; // 8px отступ
      let left = rect.right + scrollX - Math.max(220, rect.width); // выравнивание по правому краю
      // Границы экрана
      const maxLeft = scrollX + window.innerWidth - 16; // 16px паддинг
      const minLeft = scrollX + 16;
      left = Math.min(Math.max(left, minLeft), maxLeft);
      this.dropdownPosition = { top, left, width: Math.max(220, rect.width) };
    },
    
    getStatusLabel(statusClass) {
      if (!statusClass) return this.$t('case.status.none');
      const statusValue = statusClass.replace('status-', '');
      return this.statusLabelMap[statusValue] || statusValue;
    },
    normalizeStatusClass(statusClass) {
      if (!statusClass) return 'status-no-case';
      return statusClass.startsWith('status-') ? statusClass : `status-${statusClass}`;
    },
    
    getStatusLabelByValue(statusValue) {
      return this.statusLabelMap[statusValue] || statusValue;
    },
    
    setStatusFilter(status) {
      this.statusFilter = status;
      this.showStatusFilter = false;
      console.log('Установлен фильтр статуса:', status); // Для отладки
    },
    
    clearStatusFilter() {
      this.statusFilter = '';
    },
    
    canChooseManager() {
      const r = (this.currentUser.role || '').toUpperCase();
      return r === 'ADMIN' || r === 'LEAD';
    },
    async addNewClient(clientData) {
      const token = localStorage.getItem('user-token');
      try {
        // Ограничения на стороне фронта: клиенты могут создать профиль только для себя и только один раз
        if (!this.currentUser.is_manager) {
          if (!this.currentUser.is_client) {
            alert('У вас нет прав для добавления клиента.');
            return;
          }
          if (this.clients.length > 0) {
            alert('Ваш профиль клиента уже существует.');
            return;
          }
          // Принудительно выставляем email как у аккаунта
          clientData = { ...clientData, email: this.currentUser.email };
        }

        await axios.post('http://127.0.0.1:8000/api/clients/', clientData, {
          headers: { Authorization: `Token ${token}` }
        });
        // Перезагрузим список, чтобы получить корректные вычисляемые поля для таблицы
        await this.reloadClients();
        this.showAddClientModal = false;
      } catch (error) {
        const msg = error.response?.data?.detail || error.response?.data || error.message || error;
        console.error("Ошибка при добавлении клиента:", error.response?.data || error);
        if (error.response?.status === 403) {
          alert("Недостаточно прав для добавления клиента.");
        } else if (error.response?.status === 400) {
          alert(typeof msg === 'string' ? msg : 'Проверьте введенные данные.');
        } else {
          alert("Не удалось добавить клиента. Повторите попытку позже.");
        }
      }
    },
    
    openClient(clientId) {
      this.$router.push(`/dashboard/clients/${clientId}`);
    },
    
    handleClickOutside(event) {
      // Закрываем, если клик вне кнопки и вне самого телепортированного списка
      const inButton = !!event.target.closest('.filter-dropdown');
      const inDropdown = !!event.target.closest('.status-filter-dropdown');
      if (!inButton && !inDropdown) {
        this.showStatusFilter = false;
      }
    },
    formatManagerName(c){
      const first = (c.created_by_first_name || '').trim();
      const last = (c.created_by_last_name || '').trim();
      const full = `${first} ${last}`.trim();
      return full || (c.created_by_name || '-');
    },
  },
  mounted() {
    // Добавляем обработчик клика вне выпадающего списка
    document.addEventListener('click', this.handleClickOutside);
    window.addEventListener('scroll', this.updateDropdownPosition, true);
    window.addEventListener('resize', this.updateDropdownPosition);
  },
  beforeUnmount() {
    // Удаляем обработчик при уничтожении компонента
    document.removeEventListener('click', this.handleClickOutside);
    window.removeEventListener('scroll', this.updateDropdownPosition, true);
    window.removeEventListener('resize', this.updateDropdownPosition);
  }
};
</script>

<style scoped>
/* Добавляем стили для активного фильтра */
.active-filter {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 5px;
  padding: 4px 8px;
  background-color: #e8f4f0;
  border-radius: 4px;
  font-size: 12px;
  color: #4A9E80;
}

.clear-filter {
  background: none;
  border: none;
  color: #4A9E80;
  cursor: pointer;
  font-size: 16px;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.clear-filter:hover {
  background-color: #d4e8e0;
}

/* Остальные стили остаются без изменений */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

.list-view-wrapper {
  padding: 40px;
  font-family: 'Inter', sans-serif;
  position: relative;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.content-header h1 {
  font-size: 28px;
  color: #2c3e50;
  font-weight: 700;
}

/* Unified button style from Notifications (base) */
.btn { background: var(--btn-bg,#fff); border:1px solid var(--btn-border,#d0d7e2); padding:10px 20px; border-radius:8px; cursor:pointer; font-weight:600; font-family:'Inter',sans-serif; font-size:14px; transition:background .25s, color .25s, border-color .25s, box-shadow .25s; }
.btn:hover { background: var(--primary-color,#4A90E2); color:#fff; border-color: var(--primary-color,#4A90E2); }
.btn:disabled { opacity:.55; cursor:not-allowed; }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030; }
.btn.danger:hover { background:rgba(255,82,82,0.20); border-color:rgba(255,82,82,0.6); color:#a61b1b; }
.btn.danger:disabled { background:rgba(255,82,82,0.08); border-color:rgba(255,82,82,0.25); color:rgba(197,48,48,0.55); }

.search-section {
  margin-bottom: 30px;
}

.search-box {
  position: relative;
  max-width: 400px;
}

.date-filter.modern {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.date-filter .chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.chip {
  border: 1px solid var(--form-border,#e2e8f0);
  background: var(--card-bg);
  color: #334155;
  padding: 6px 12px;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: all .2s ease;
}
.chip:hover { background: #f7f9fc; }
.chip.active { background: #e8f4f0; border-color: #c7e6db; color: #2f7f66; }

.custom-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.custom-range .date-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
}

.custom-range .date-input {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  font-family: 'Inter', sans-serif;
  font-size: 13px;
  color: #4b5563; /* grey text */
  background: #ffffff; /* white background */
  border: 1px solid #cbd5e1; /* slate-300 */
  border-radius: 10px;
  padding: 10px 12px;
  line-height: 1.2;
  box-shadow: 0 1px 0 rgba(0,0,0,0.02) inset;
}
.custom-range .date-input:focus {
  outline: none;
  border-color: #4A9E80;
  box-shadow: 0 0 0 2px rgba(74,158,128,.12);
  background: #ffffff; /* keep white on focus */
}
/* Placeholder like dd.mm.yyyy look */
.custom-range .date-input::-webkit-datetime-edit { font-family: 'Inter', sans-serif; color: #4b5563; }
.custom-range .date-input::-webkit-datetime-edit-fields-wrapper { padding: 0; }
.custom-range .date-input::-webkit-datetime-edit-month-field,
.custom-range .date-input::-webkit-datetime-edit-day-field,
.custom-range .date-input::-webkit-datetime-edit-year-field { padding: 0 2px; }
.custom-range .date-input::-webkit-calendar-picker-indicator {
  cursor: pointer;
  opacity: 0.7;
  filter: grayscale(100%);
}
.custom-range .date-input:hover::-webkit-calendar-picker-indicator { opacity: 1; filter: none; }

.clear-chip {
  border: none;
  background: transparent;
  color: #111827; /* black/dark */
  cursor: pointer;
  font-weight: 400; /* normal */
}
.clear-chip:hover { color:#000; text-decoration: underline; }

/* Modern manager filter */
.creator-filter {
  margin-top: 10px;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--card-bg);
  border: 1px solid #e0e6ed;
  border-radius: 10px;
}
.creator-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #5a6a7b;
  font-weight: 600;
}
.creator-select { padding:8px 10px; }
.creator-clear {
  font-size: 12px;
}

.search-input { width:100%; padding:8px 36px 8px 12px; }

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #5a6a7b;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none; /* не блокируем клики по инпуту */
}

/* Подсветка иконки при фокусе поля */
.search-input:focus + .search-icon {
  color: var(--primary-color);
}

.status-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-dropdown {
  position: relative;
  display: inline-block;
}

.filter-button {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease;
}

.filter-button:hover {
  background-color: #f0f0f0;
}

.filter-button.active {
  color: #4A9E80;
  background-color: #e8f4f0;
}

.filter-dropdown-content {
  position: fixed; /* Телепортируем и фиксируем на вьюпорте */
  background: var(--card-bg);
  border: 1px solid #e0e6ed;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  padding: 8px 0;
  z-index: 4000; /* Выше всего контента таблицы */
  min-width: 220px;
  max-height: 60vh;
  overflow-y: auto;
  overflow-x: hidden; /* убираем горизонтальный скролл */
  max-width: calc(100vw - 32px);
  box-sizing: border-box;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  cursor: pointer;
  border-radius: 0;
  transition: background-color 0.2s ease;
  white-space: nowrap;
  border: none;
  width: 100%;
  text-align: left;
  background: none;
  font-size: 14px;
  overflow: hidden; /* текст не раздувает ширину */
  text-overflow: ellipsis; /* многий текст с троеточием */
}

.filter-option:hover {
  background-color: #f7f9fc;
}

.filter-option.active {
  background-color: #e8f4f0;
  color: #4A9E80;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.status-indicator.all-status {
  background-color: #6b7280;
}

.status-preparation { background-color: #8b5cf6; }
.status-submitted { background-color: #0284c7; }
.status-in_progress { background-color: #ca8a04; }
.status-decision_positive { background-color: #16a34a; }
.status-decision_negative { background-color: #dc2626; }
.status-closed { background-color: #4b5563; }
.status-no-case { background-color: #6b7280; }

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  background: transparent;
}

.clients-table {
  width: 100%;
  border-collapse: collapse;
  background-color: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.07);
  overflow: hidden;
  font-family: 'Inter', sans-serif;
  position: relative;
  z-index: 1;
}

.clients-table th, .clients-table td {
  padding: 16px 20px;
  text-align: left;
}

.clients-table th {
  background-color: #f7f9fc;
  font-size: 14px;
  color: #5a6a7b;
  font-weight:700;
  position: relative;
}

.clients-table th.sortable {
  cursor: pointer;
  user-select: none;
}
.sortable-label { margin-right: 6px; }
.sort-icon { display: inline-flex; vertical-align: middle; color: #6b7280; }

.clients-table td {
  border-top: 1px solid #e0e6ed;
  font-size: 15px;
}

.client-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

/* Зебра: чётные строки слегка темнее, нечётные белые */
.clients-table tbody tr.client-row:nth-child(even) {
  background-color: #f7f9fc;
}

/* Ховер немного темнее, чтобы было видно наведение на обеих полосах */
.client-row:hover {
  background-color: #eef3f9;
}

.no-results-row {
  pointer-events: none;
}

.no-results {
  text-align: center;
  color: #6b7280;
  font-style: italic;
  padding: 40px !important;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 20px;
  font-weight: 600;
  font-size: 13px;
  white-space: nowrap;
}

.status-preparation { background-color: #f3e8ff; color: #8b5cf6; }
.status-submitted { background-color: #e0f2fe; color: #0284c7; }
.status-in_progress { background-color: #fef9c3; color: #ca8a04; }
.status-decision_positive { background-color: #dcfce7; color: #16a34a; }
.status-decision_negative { background-color: #fee2e2; color: #dc2626; }
.status-closed { background-color: #e5e7eb; color: #4b5563; }
.status-no-case { background-color: #f3f4f6; color: #6b7280; }

.loader, .empty-state {
  text-align: center;
  padding: 40px;
  color: #5a6a7b;
  font-family: 'Inter', sans-serif;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}

@media (max-width: 768px) {
  .content-header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .search-box {
    max-width: 100%;
  }
  
  .filter-dropdown-content {
    left: 16px !important;
    right: 16px !important;
    min-width: auto !important;
  }
}
</style>