<template>
  <div class="list-view-wrapper">
    <header class="content-header">
      <h1>Клиенты</h1>
      <button @click="showAddClientModal = true" class="button primary">Добавить клиента</button>
    </header>

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
            <th>Статус дела</th>
            <th>Действия</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="client in clients" :key="client.id">
            <td>{{ client.first_name }} {{ client.last_name }}</td>
            <td>{{ client.email }}</td>
            <td>{{ client.phone_number }}</td>
            <td>
              <span class="status-badge" :class="client.active_case_status_class">
                {{ client.active_case_status }}
              </span>
            </td>
            <td>
              <router-link :to="`/dashboard/clients/${client.id}`" class="button-icon view-details">
                Открыть
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <AddClientModal 
    v-if="showAddClientModal" 
    @close="showAddClientModal = false" 
    @save="addNewClient"
  />
</template>

<script>
import axios from 'axios';
// 3. Импортируем компонент модального окна
import AddClientModal from '@/components/AddClientModal.vue';

export default {
  name: 'ClientListView',
  // 4. Регистрируем компонент
  components: {
    AddClientModal
  },
  data() {
    return {
      clients: [],
      loading: true,
      // 5. Добавляем переменную для управления видимостью окна
      showAddClientModal: false,
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
  // 6. Добавляем метод для сохранения нового клиента
  methods: {
    async addNewClient(clientData) {
      const token = localStorage.getItem('user-token');
      try {
        const response = await axios.post('http://127.0.0.1:8000/api/clients/', clientData, {
          headers: { Authorization: `Token ${token}` }
        });
        
        // Добавляем нового клиента в начало списка без перезагрузки страницы
        this.clients.unshift(response.data);
        this.showAddClientModal = false; // Закрываем окно
      } catch (error) {
        console.error("Ошибка при добавлении клиента:", error.response.data);
        // Здесь можно добавить логику отображения ошибки пользователю
        alert("Не удалось добавить клиента. Проверьте введенные данные.");
      }
    }
  }
};
</script>

<style scoped>
/* Стили остаются без изменений */
.list-view-wrapper {
  padding: 40px;
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
  background-color: #4A90E2;
  color: #ffffff;
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.clients-table {
  width: 100%;
  border-collapse: collapse;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.07);
  overflow: hidden;
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
}
.clients-table td {
  border-top: 1px solid #e0e6ed;
  font-size: 15px;
}
.status-badge {
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 12px;
  text-transform: capitalize;
}
.preparation { background-color: #e0f2fe; color: #0284c7; }
.submitted { background-color: #dbeafe; color: #4f46e5; }
.in_progress { background-color: #fef9c3; color: #ca8a04; }

.button-icon {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #cdd4de;
  background-color: #fff;
  cursor: pointer;
  font-weight: 500;
  text-decoration: none;
  color: #2c3e50;
}
</style>