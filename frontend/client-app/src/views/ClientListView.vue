<template>
  <div class="list-view-wrapper">
    <header class="content-header">
      <h1>Клиенты</h1>
      <button @click="showAddClientModal = true" class="button primary">Добавить клиента</button>
    </header>

    <div class="search-section">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Поиск по имени, фамилии, email, телефону..." 
          class="search-input"
        >
        <span class="search-icon">🔍</span>
      </div>
    </div>

    <div class="content-body">
      <div v-if="loading" class="loader">Загрузка...</div>
      
      <div v-if="!loading && clients.length === 0" class="empty-state">
        <p>У вас еще нет клиентов. Нажмите "Добавить клиента", чтобы начать.</p>
      </div>
      
      <table v-if="!loading && clients.length > 0" class="clients-table">
        <thead>
          <tr>
            <th>Имя и Фамилия</th>
            <th>Email</th>
            <th>Телефон</th>
            <th>
              <div class="status-header">
                <span>Статус дела</span>
                <div class="filter-dropdown">
                  <button class="filter-button" @click="toggleStatusFilter">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path d="M6 9l6 6 6-6"/>
                    </svg>
                  </button>
                  <div v-if="showStatusFilter" class="filter-dropdown-content">
                    <div 
                      class="filter-option"
                      :class="{ active: statusFilter === '' }"
                      @click="setStatusFilter('')"
                    >
                      <span class="status-indicator all-status"></span>
                      Все статусы
                    </div>
                    <div 
                      v-for="status in statusOptions" 
                      :key="status.value"
                      class="filter-option"
                      :class="{ active: statusFilter === status.value }"
                      @click="setStatusFilter(status.value)"
                    >
                      <span class="status-indicator" :class="`status-${status.value}`"></span>
                      {{ status.label }}
                    </div>
                  </div>
                </div>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredClients.length === 0" class="no-results-row">
            <td colspan="4" class="no-results">Клиенты по вашему запросу не найдены</td>
          </tr>
          <tr v-for="client in filteredClients" :key="client.id" class="client-row" @click="openClient(client.id)">
            <td>{{ client.first_name }} {{ client.last_name }}</td>
            <td>{{ client.email }}</td>
            <td>{{ client.phone_number }}</td>
            <td>
              <span class="status-badge" :class="client.active_case_status_class">
                {{ getStatusLabel(client.active_case_status_class) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Overlay для закрытия выпадающего списка -->
    <div v-if="showStatusFilter" class="dropdown-overlay" @click="showStatusFilter = false"></div>
  </div>

  <AddClientModal 
    v-if="showAddClientModal" 
    @close="showAddClientModal = false" 
    @save="addNewClient"
  />
</template>

<script>
import axios from 'axios';
import AddClientModal from '@/components/AddClientModal.vue';

export default {
  name: 'ClientListView',
  components: {
    AddClientModal
  },
  data() {
    return {
      clients: [],
      loading: true,
      showAddClientModal: false,
      searchQuery: '',
      statusFilter: '',
      showStatusFilter: false,
      statusOptions: [
        { value: 'preparation', label: 'Подготовка' },
        { value: 'submitted', label: 'Подано' },
        { value: 'in_progress', label: 'В процессе' },
        { value: 'decision_positive', label: 'Положительное решение' },
        { value: 'decision_negative', label: 'Отрицательное решение' },
        { value: 'closed', label: 'Закрыто' },
        { value: 'no-case', label: 'Нет дела' }
      ],
      statusLabelMap: {
        'preparation': 'Подготовка',
        'submitted': 'Подано',
        'in_progress': 'В процессе',
        'decision_positive': 'Положительное решение',
        'decision_negative': 'Отрицательное решение',
        'closed': 'Закрыто',
        'no-case': 'Нет дела'
      }
    };
  },
  async created() {
    const token = localStorage.getItem('user-token');
    if (!token) {
      this.$router.push('/login');
      return;
    }

    try {
      const response = await axios.get('http://127.0.0.1:8000/api/clients/', {
        headers: { Authorization: `Token ${token}` }
      });
      this.clients = response.data;
    } catch (error) {
      console.error("Ошибка при загрузке списка клиентов:", error);
    } finally {
      this.loading = false;
    }
  },
  computed: {
    filteredClients() {
      let filtered = this.clients;

      // Поиск по всем параметрам
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase().trim();
        filtered = filtered.filter(client => {
          const fullName = `${client.first_name || ''} ${client.last_name || ''}`.toLowerCase();
          return fullName.includes(query) ||
                 client.email?.toLowerCase().includes(query) ||
                 client.phone_number?.includes(query);
        });
      }

      // Фильтр по статусу
      if (this.statusFilter) {
        filtered = filtered.filter(client => {
          // Получаем значение статуса из класса
          const statusClass = client.active_case_status_class;
          if (!statusClass) return false;
          
          // Извлекаем название статуса из класса (убираем 'status-')
          const statusValue = statusClass.replace('status-', '');
          return statusValue === this.statusFilter;
        });
      }

      return filtered;
    }
  },
  methods: {
    toggleStatusFilter() {
      this.showStatusFilter = !this.showStatusFilter;
    },
    
    getStatusLabel(statusClass) {
      if (!statusClass) return 'Не указан';
      const statusValue = statusClass.replace('status-', '');
      return this.statusLabelMap[statusValue] || statusValue;
    },
    
    setStatusFilter(status) {
      this.statusFilter = status;
      this.showStatusFilter = false;
    },
    
    async addNewClient(clientData) {
      const token = localStorage.getItem('user-token');
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/clients/', clientData, {
          headers: { Authorization: `Token ${token}` }
        });
        
        this.clients.unshift(response.data);
        this.showAddClientModal = false;
      } catch (error) {
        console.error("Ошибка при добавлении клиента:", error.response.data);
        alert("Не удалось добавить клиента. Проверьте введенные данные.");
      }
    },
    
    openClient(clientId) {
      this.$router.push(`/dashboard/clients/${clientId}`);
    }
  },
  mounted() {
    // Закрываем выпадающий список при клике вне его
    document.addEventListener('click', (e) => {
      if (!e.target.closest('.filter-dropdown')) {
        this.showStatusFilter = false;
      }
    });
  }
};
</script>

<style scoped>
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

.button.primary {
  background-color: #4A9E80;
  color: #ffffff;
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  font-family: 'Inter', sans-serif;
  transition: background-color 0.2s ease;
}

.button.primary:hover {
  background-color: #428f74;
}

/* Стили для поиска */
.search-section {
  margin-bottom: 30px;
}

.search-box {
  position: relative;
  max-width: 400px;
}

.search-input {
  width: 100%;
  padding: 12px 40px 12px 16px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  transition: border-color 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: #4A9E80;
  box-shadow: 0 0 0 2px rgba(74, 158, 128, 0.1);
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #5a6a7b;
}

/* Стили для фильтра статуса */
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

.filter-dropdown-content {
  position: fixed;
  background: white;
  border: 1px solid #e0e6ed;
  border-radius: 8px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
  padding: 8px 0;
  z-index: 1001;
  min-width: 220px;
  max-height: none;
  overflow: visible;
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

/* Overlay для закрытия выпадающего списка */
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
  background-color: white;
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
  font-weight: 600;
  position: relative;
}

.clients-table td {
  border-top: 1px solid #e0e6ed;
  font-size: 15px;
}

.client-row {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.client-row:hover {
  background-color: #f7f9fc;
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

/* Адаптивность для мобильных устройств */
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
    right: 20px;
    left: 20px;
    min-width: auto;
  }
}
</style>