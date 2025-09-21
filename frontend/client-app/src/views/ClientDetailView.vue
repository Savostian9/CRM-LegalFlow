<template>
  <div v-if="loading" class="loader">Загрузка...</div>
  <div v-if="!loading && editableClient" class="client-card-wrapper">
    <header class="card-header">
      <div class="header-left">
        <router-link to="/dashboard/clients" class="back-button">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" d="M7.72 12.53a.75.75 0 0 1 0-1.06l7.5-7.5a.75.75 0 1 1 1.06 1.06L9.31 12l6.97 6.97a.75.75 0 1 1-1.06 1.06l-7.5-7.5Z" clip-rule="evenodd" />
          </svg>
          <span>Назад к списку</span>
        </router-link>
        <h1>Карточка клиента: {{ editableClient.first_name }} {{ editableClient.last_name }}</h1>
      </div>
      <div v-if="editableCase" class="case-status" :class="caseStatusClass">
        {{ getStatusDisplay(editableCase.status) }}
      </div>
    </header>

    <form @submit.prevent="saveAllChanges" class="card-content">
      <section class="data-section">
        <h3>Личные данные</h3>
        <div class="data-grid">
          <div class="data-item"><label>Имя</label><input type="text" v-model="editableClient.first_name" /></div>
          <div class="data-item"><label>Фамилия</label><input type="text" v-model="editableClient.last_name" /></div>
          <div class="data-item"><label>Телефон</label><vue-tel-input v-model="editableClient.phone_number" mode="international"></vue-tel-input></div>
          <div class="data-item"><label>Email</label><input type="email" v-model="editableClient.email" /></div>
          <div class="data-item full-width"><label>Адрес</label><textarea v-model="editableClient.address"></textarea></div>
        </div>
      </section>

      <div v-if="!editableCase" class="empty-state">
        <p>У этого клиента еще нет дел.</p>
        <button type="button" @click="startNewCase" class="button primary">Создать новое дело</button>
      </div>

      <template v-else>
        <section class="data-section">
          <h3>Данные по делу о легализации</h3>
          <div class="data-grid">
            <div class="data-item"><label>Дата подачи</label><input type="date" v-model="editableCase.submission_date" /></div>
            <div class="data-item"><label>Дата решения</label><input type="date" v-model="editableCase.decision_date" /></div>
            <div class="data-item full-width" :class="caseStatusClass">
              <label>Статус дела</label>
              <select v-model="editableCase.status">
                <option value="PREPARATION">Подготовка документов</option>
                <option value="SUBMITTED">Подано</option>
                <option value="IN_PROGRESS">На рассмотрении</option>
                <option value="DECISION_POSITIVE">Решение положительное</option>
                <option value="DECISION_NEGATIVE">Решение отрицательное</option>
                <option value="CLOSED">Дело закрыто</option>
              </select>
            </div>
          </div>
        </section>

        <section class="data-section">
          <h3>Чек-лист поданных документов</h3>
          <ul class="document-checklist">
            <li v-for="(doc, index) in editableCase.documents" :key="index" class="document-item">
              <div class="doc-info">
                <input type="checkbox" v-model="doc.status" true-value="SUBMITTED" false-value="NOT_SUBMITTED">
                <span class="doc-name">{{ getDocumentTypeDisplay(doc.document_type) }}</span>
              </div>
              <div class="doc-actions">
                <button type="button" v-if="doc.file" class="button-icon view-doc">Посмотреть</button>
                <button type="button" class="button-icon upload-doc">Загрузить</button>
              </div>
            </li>
          </ul>
        </section>
      </template>

      <footer class="card-footer" v-if="editableCase">
        <button type="submit" class="button primary save-button">Сохранить все изменения</button>
      </footer>
    </form>
  </div>
</template>

<script>
import axios from 'axios';
import { cloneDeep } from 'lodash';

export default {
  name: 'ClientDetailView',
  props: ['id'],
  data() {
    return {
      loading: true,
      client: null,
      editableClient: null,
      editableCase: null,
      statusMap: { 'PREPARATION': 'Подготовка документов', 'SUBMITTED': 'Подано', 'IN_PROGRESS': 'На рассмотрении', 'DECISION_POSITIVE': 'Решение положительное', 'DECISION_NEGATIVE': 'Решение отрицательное', 'CLOSED': 'Дело закрыто' },
      docTypeMap: { 'ZALACZNIK_1': 'Załącznik nr 1', 'UMOWA_PRACA': 'Umowa o pracę / zlecenia', 'UMOWA_NAJMU': 'Umowa najmu', 'ZUS_ZUA_ZZA': 'ZUS ZUA / ZZA', 'ZUS_RCA_DRA': 'ZUS RCA/DRA', 'POLISA': 'Polisa ubezpieczeniowa', 'ZASWIADCZENIE_US': 'Zaświadczenie z Urzędu Skarbowego', 'ZASWIADCZENIA_ZUS': 'Zaświadczenia ZUS pracodawcy', 'PIT_37': 'PIT 37', 'BADANIE_LEKARSKIE': 'Badanie lekarskie', 'SWIADECTWO_KIEROWCY': 'Świadectwo kierowcy', 'PRAWO_JAZDY': 'Prawo jazdy', 'INNE': 'Другое' }
    };
  },
  computed: {
    caseStatusClass() {
      return this.editableCase ? `status-${this.editableCase.status.toLowerCase()}` : '';
    }
  },
  async created() {
    this.fetchClientData();
  },
  methods: {
    async fetchClientData() {
      const token = localStorage.getItem('user-token');
      if (!token) { this.$router.push('/login'); return; }
      
      this.loading = true;
      try {
        const response = await axios.get(`http://127.0.0.1:8000/api/clients/${this.id}/`, {
          headers: { Authorization: `Token ${token}` }
        });
        this.client = response.data;
        this.resetEditableData();
      } catch (error) {
        console.error("Ошибка при загрузке данных клиента:", error);
      } finally {
        this.loading = false;
      }
    },
    resetEditableData() {
      this.editableClient = cloneDeep(this.client);
      if (this.client.legal_cases && this.client.legal_cases.length > 0) {
        this.editableCase = cloneDeep(this.client.legal_cases[0]);
      } else {
        this.editableCase = null;
      }
    },
    startNewCase() {
      this.editableCase = {
        submission_date: new Date().toISOString().slice(0, 10),
        decision_date: null,
        status: 'PREPARATION',
        documents: Object.keys(this.docTypeMap).map(key => ({
          document_type: key,
          status: 'NOT_SUBMITTED'
        }))
      };
    },
    async saveAllChanges() {
        const token = localStorage.getItem('user-token');
        const payload = {
            ...this.editableClient,
            legal_cases: [this.editableCase]
        };
        try {
            const response = await axios.put(`http://127.0.0.1:8000/api/clients/${this.id}/`, payload, {
                headers: { Authorization: `Token ${token}` }
            });
            this.client = response.data;
            this.resetEditableData();
            alert('Данные успешно сохранены!');
        } catch (error) {
            console.error("Ошибка сохранения:", error.response?.data || error);
            alert("Не удалось сохранить данные.");
        }
    },
    getStatusDisplay(statusKey) {
        return this.statusMap[statusKey] || statusKey;
    },
    getDocumentTypeDisplay(docKey) {
        return this.docTypeMap[docKey] || docKey;
    }
  }
};
</script>

<style scoped>
:root {
  --primary-color: #4A9E80;
  --dark-blue: #2c3e50;
  --text-color: #5a6a7b;
  --background-color: #f7f9fc;
  --white-color: #ffffff;
  /* Еле заметный, но выделяющийся стиль для рамок */
  --input-border-color: #e0e6ed;
  --input-shadow: inset 0 1px 2px rgba(0,0,0,0.07);
  --border-color-light: #e0e6ed; /* Для разделителей */
}

.client-card-wrapper {
  background-color: var(--white-color);
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.07);
  overflow: hidden;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 30px;
  background-color: var(--background-color);
  border-bottom: 1px solid var(--border-color-light);
  gap: 20px;
}

.header-left {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 6px;
  background-color: #eef2f7;
  color: var(--text-color);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.back-button:hover { background-color: #e0e6ed; }
.back-button svg { width: 20px; height: 20px; }
.card-header h1 { font-size: 22px; color: var(--dark-blue); margin: 0; }

.case-status {
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

.card-content {
  padding: 30px;
}

.data-section {
  margin-bottom: 40px;
}
.data-section:last-child {
  margin-bottom: 0;
}
.data-section h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--dark-blue);
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--border-color-light);
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 25px;
}

.data-item .label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 14px;
  color: var(--dark-blue);
}

.data-item .value {
  font-size: 15px;
  padding: 12px 15px;
  background-color: var(--background-color);
  border-radius: 8px;
  min-height: 48px;
  display: flex;
  align-items: center;
  box-sizing: border-box;
  border: 1px solid var(--input-border-color);
  box-shadow: var(--input-shadow);
}

.data-item input,
.data-item textarea,
.data-item select,
.data-item :deep(.vue-tel-input) {
  width: 100%;
  min-height: 48px;
  padding: 12px 15px;
  border: 1px solid var(--input-border-color);
  box-shadow: var(--input-shadow);
  border-radius: 8px;
  box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  background-color: var(--white-color);
}
.data-item textarea {
  height: auto;
  min-height: 80px;
}
.data-item :deep(.vti__input) {
  min-height: 46px;
  border: none;
  box-shadow: none;
  background-color: transparent;
}
.data-item :deep(.vti__dropdown) {
  padding: 11px;
}
.data-item :deep(.vue-tel-input) {
  border: 1px solid var(--input-border-color);
  box-shadow: var(--input-shadow);
}
.data-item :deep(.vue-tel-input.focus) {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 158, 128, 0.2);
}

.data-item input:focus,
.data-item textarea:focus,
.data-item select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(74, 158, 128, 0.2);
}
.data-item.full-width {
  grid-column: 1 / -1;
}

.data-item.status-preparation select, .data-item.status-preparation .value {
  border-color: #c084fc; background-color: #faf5ff;
}
.data-item.status-submitted select, .data-item.status-submitted .value {
  border-color: #7dd3fc; background-color: #f0f9ff;
}
.data-item.status-in_progress select, .data-item.status-in_progress .value {
  border-color: #fcd34d; background-color: #fffbeb;
}
.data-item.status-decision_positive select, .data-item.status-decision_positive .value {
  border-color: #86efac; background-color: #f0fdf4;
}
.data-item.status-decision_negative select, .data-item.status-decision_negative .value {
  border-color: #fca5a5; background-color: #fef2f2;
}
.data-item.status-closed select, .data-item.status-closed .value {
  border-color: #d1d5db; background-color: #f9fafb;
}

.document-checklist {
  list-style: none;
  padding: 0;
}

.document-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 10px;
  border-bottom: 1px solid #eef2f7;
  transition: background-color 0.2s ease;
}
.document-item:last-child {
  border-bottom: none;
}
.document-item:hover {
  background-color: #f7f9fc;
}
.doc-info {
  display: flex;
  align-items: center;
  gap: 15px;
}
.doc-info input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}
.doc-name {
  font-size: 15px;
}
.other-doc-input {
  border: 1px solid var(--input-border-color);
  padding: 5px;
  border-radius: 6px;
}

.doc-actions {
  display: flex;
  gap: 10px;
}
.button-icon {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid var(--input-border-color);
  background-color: #fff;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}
.button-icon.upload-doc:hover {
  background-color: #eef2f7;
  color: var(--dark-blue);
  border-color: var(--dark-blue);
}
.button-icon.view-doc {
  color: #1e8e3e;
}

.empty-state, .loader {
  text-align: center;
  padding: 40px;
  color: #5a6a7b;
}

.empty-state p {
  margin-bottom: 20px;
}
.button {
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}
.button.primary {
  background-color: var(--primary-color);
  color: var(--white-color);
}
.button.secondary {
  background-color: #f0f2f5;
  color: var(--dark-blue);
}
.button.secondary:hover {
  background-color: #e4e6e9;
}
.add-other-btn {
  margin-top: 15px;
}
.card-footer {
  padding: 20px 30px;
  text-align: right;
  border-top: 1px solid var(--border-color-light);
  background-color: var(--background-color);
}
.save-button {
  font-size: 16px;
}
</style>