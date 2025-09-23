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
    </header>

    <form @submit.prevent class="card-content">
      <!-- Скрытое поле для загрузки файлов -->
      <input 
        type="file" 
        style="display: none" 
        ref="fileInput" 
        @change="handleFileUpload"
      >

      <section class="data-section">
        <h3>Личные данные</h3>
        <div class="data-grid">
          <div class="data-item"><label>Имя</label><input type="text" v-model="editableClient.first_name" @change="saveAllChanges" /></div>
          <div class="data-item"><label>Фамилия</label><input type="text" v-model="editableClient.last_name" @change="saveAllChanges" /></div>
          <div class="data-item"><label>Телефон</label><vue-tel-input v-model="editableClient.phone_number" mode="international" @blur="saveAllChanges"></vue-tel-input></div>
          <div class="data-item"><label>Email</label><input type="email" v-model="editableClient.email" @change="saveAllChanges" /></div>
          <div class="data-item"><label>Адрес</label><textarea v-model="editableClient.address" @change="saveAllChanges"></textarea></div>

          <div class="data-item"><label>Номер паспорта</label><input type="text" v-model="editableClient.passport_number" @change="saveAllChanges" /></div>
          <div class="data-item"><label>Паспорт действителен до</label><input type="date" v-model="editableClient.passport_expiry_date" @change="saveAllChanges" /></div>
          <div class="data-item"><label>Тип текущей визы</label><input type="text" v-model="editableClient.current_visa_type" @change="saveAllChanges" /></div>
          <div class="data-item"><label>Виза действительна до</label><input type="date" v-model="editableClient.current_visa_expiry_date" @change="saveAllChanges" /></div>
        </div>
      </section>

      <div v-if="!editableClient.legal_cases || editableClient.legal_cases.length === 0" class="empty-state">
        <p>У этого клиента еще нет дел.</p>
      </div>

      <div v-else class="cases-container">
        <div v-for="(legalCase, caseIndex) in editableClient.legal_cases" :key="caseIndex" class="case-wrapper">
          <div class="case-header" @click="toggleCase(caseIndex)">
            <div class="case-header-title">
              <svg class="toggle-icon" :class="{ 'is-expanded': legalCase._isExpanded }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 0 1 .02-1.06L11.168 10 7.23 6.29a.75.75 0 1 1 1.04-1.08l4.5 4.25a.75.75 0 0 1 0 1.08l-4.5 4.25a.75.75 0 0 1-1.06-.02Z" clip-rule="evenodd" />
              </svg>
              <h4>Дело №{{ caseIndex + 1 }}: {{ getCaseTypeDisplay(legalCase.case_type) }}</h4>
            </div>
            <div class="case-status" :class="getCaseStatusClass(legalCase)">
              {{ getStatusDisplay(legalCase.status) }}
            </div>
          </div>

          <div v-if="legalCase._isExpanded" class="case-details">
            <section class="data-section">
              <h3>Данные по делу о легализации</h3>
              <div class="data-grid">
                <div class="data-item full-width">
                  <label>Вид дела</label>
                  <select v-model="legalCase.case_type" @change="saveAllChanges">
                    <option value="CZASOWY_POBYT">ВНЖ (Czasowy pobyt)</option>
                    <option value="STALY_POBYT">ПМЖ (Staly pobyt)</option>
                    <option value="REZydent_UE">Карта резидента ЕС (Karta rezydenta UE)</option>
                    <option value="OBYWATELSTWO">Гражданство (Obywatelstwo)</option>
                  </select>
                </div>
                <div class="data-item"><label>Дата подачи</label><input type="date" v-model="legalCase.submission_date" @change="saveAllChanges" /></div>
                <div class="data-item"><label>Дата решения</label><input type="date" v-model="legalCase.decision_date" @change="saveAllChanges" /></div>
                <div class="data-item full-width">
                  <label>Статус дела</label>
                  <select v-model="legalCase.status" @change="saveAllChanges">
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
                <li v-for="(doc, docIndex) in legalCase.documents" :key="docIndex" class="document-item">
                  <div class="doc-info">
                    <input type="checkbox" v-model="doc.status" true-value="SUBMITTED" false-value="NOT_SUBMITTED" @change="saveAllChanges">
                    <input v-if="doc.isNew" type="text" v-model="doc.document_type" placeholder="Название документа" class="other-doc-input" @change="saveAllChanges">
                    <span v-else class="doc-name">{{ getDocumentTypeDisplay(doc.document_type) }}</span>
                  </div>
                  <div class="doc-actions">
                    <div v-if="doc.files && doc.files.length > 0" class="uploaded-files">
                      <div v-for="(file, fileIndex) in doc.files" :key="fileIndex" class="file-chip">
                        <span @click="viewFile(file)" class="file-name">{{ file.name }}</span>
                        <button type="button" @click="removeUploadedFile(legalCase, docIndex, fileIndex)" class="delete-file-btn">&times;</button>
                      </div>
                    </div>
                    <button type="button" @click="triggerUpload(caseIndex, docIndex)" class="button-icon upload-doc">Загрузить</button>
                    <button type="button" @click="removeDocument(caseIndex, docIndex)" class="button-icon delete-doc" title="Удалить строку">
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-5 h-5">
                        <path d="M6.28 5.22a.75.75 0 0 0-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 1 0 1.06 1.06L10 11.06l3.72 3.72a.75.75 0 1 0 1.06-1.06L11.06 10l3.72-3.72a.75.75 0 0 0-1.06-1.06L10 8.94 6.28 5.22Z" />
                      </svg>
                    </button>
                  </div>
                </li>
              </ul>
              <button type="button" @click="addDocument(caseIndex)" class="button secondary add-other-btn">Добавить документ</button>
            </section>
            <footer class="case-footer">
                <button type="button" @click="removeCase(caseIndex)" class="button-icon delete-doc">Удалить дело</button>
            </footer>
          </div>
        </div>
      </div>

      <footer class="card-footer">
        <button type="button" @click="startNewCase" class="button secondary">Добавить новое дело</button>
      </footer>
    </form>

    <!-- Custom Confirm Dialog -->
    <div v-if="showConfirmDialog" class="confirm-dialog-overlay">
      <div class="confirm-dialog">
        <p>{{ confirmDialogMessage }}</p>
        <div class="confirm-dialog-actions">
          <button @click="confirmAction" class="button primary">Да, удалить</button>
          <button @click="cancelAction" class="button secondary">Отмена</button>
        </div>
      </div>
    </div>
  </div>

  <!-- Notification Toast -->
  <transition name="toast-fade">
    <div v-if="showNotification" :class="['toast-notification', notificationType]">
      {{ notificationMessage }}
    </div>
  </transition>
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
      statusMap: { 'PREPARATION': 'Подготовка документов', 'SUBMITTED': 'Подано', 'IN_PROGRESS': 'На рассмотрении', 'DECISION_POSITIVE': 'Решение положительное', 'DECISION_NEGATIVE': 'Решение отрицательное', 'CLOSED': 'Дело закрыто' },
      caseTypeMap: { 'CZASOWY_POBYT': 'ВНЖ (Czasowy pobyt)', 'STALY_POBYT': 'ПМЖ (Staly pobyt)', 'REZydent_UE': 'Карта резидента ЕС', 'OBYWATELSTWO': 'Гражданство' },
      docTypeMap: { 'ZALACZNIK_1': 'Załącznik nr 1', 'UMOWA_PRACA': 'Umowa o pracę / zlecenia', 'UMOWA_NAJMU': 'Umowa najmu', 'ZUS_ZUA_ZZA': 'ZUS ZUA / ZZA', 'ZUS_RCA_DRA': 'ZUS RCA/DRA', 'POLISA': 'Polisa ubezpieczeniowa', 'ZASWIADCZENIE_US': 'Zaświadczenie z Urzędu Skarbowego', 'ZASWIADCZENIA_ZUS': 'Zaświadczenia ZUS работадателя', 'PIT_37': 'PIT 37', 'BADANIE_LEKARSKIE': 'Badание лекарское', 'BADANIE_MEDYCZNE': 'Badanie medyczne', 'SWIADECTWO_KIEROWCY': 'Świadectwo kierowcy' },
      uploadingDocContext: null, // { caseIndex, docIndex }
      showConfirmDialog: false,
      confirmDialogMessage: '',
      confirmCallback: null,
      showNotification: false,
      notificationMessage: '',
      notificationType: 'success', // 'success' or 'error'
      isSaving: false,
      fileInputs: [], // Для хранения ссылок на инпуты файлов
      currentUploadInfo: null, // { caseIndex, docIndex }
    };
  },
  created() {
    this.fetchClientData();
  },
  methods: {
    setFileInputRef(el) {
      if (el) {
        this.fileInputs.push(el);
      }
    },
    toggleCase(index) {
      const legalCase = this.editableClient.legal_cases[index];
      legalCase._isExpanded = !legalCase._isExpanded;
    },
    getCaseStatusClass(legalCase) {
      return legalCase ? `status-${legalCase.status.toLowerCase()}` : '';
    },
    showToast(message, type = 'success', duration = 3000) {
      this.notificationMessage = message;
      this.notificationType = type;
      this.showNotification = true;
      setTimeout(() => {
        this.showNotification = false;
      }, duration);
    },
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
        this.showToast('Ошибка при загрузке данных клиента', 'error');
      } finally {
        this.loading = false;
      }
    },
    resetEditableData() {
        this.editableClient = cloneDeep(this.client);
        if (!this.editableClient.legal_cases) {
            this.editableClient.legal_cases = [];
        }

        const hasMultipleCases = this.editableClient.legal_cases.length > 1;

        this.editableClient.legal_cases.forEach((legalCase, index) => {
            legalCase._isExpanded = hasMultipleCases ? index === 0 : false;

            const allDocTypes = Object.keys(this.docTypeMap);
            const docMap = new Map(legalCase.documents.map(doc => [doc.document_type, doc]));

            const finalDocs = allDocTypes.map(docType => {
                if (docMap.has(docType)) {
                    const existingDoc = docMap.get(docType);
                    if (!existingDoc.files) existingDoc.files = [];
                    return existingDoc;
                } else {
                    return { document_type: docType, status: 'NOT_SUBMITTED', files: [] };
                }
            });

            legalCase.documents.forEach(doc => {
                if (!allDocTypes.includes(doc.document_type)) {
                    if (!doc.files) doc.files = [];
                    finalDocs.push(doc);
                }
            });
            legalCase.documents = finalDocs;
        });
    },
    startNewCase() {
      const newCase = {
        case_type: 'CZASOWY_POBYT',
        submission_date: new Date().toISOString().slice(0, 10),
        decision_date: null,
        status: 'PREPARATION',
        documents: Object.keys(this.docTypeMap).map(key => ({
          document_type: key,
          status: 'NOT_SUBMITTED',
          files: [],
          isNew: false
        })),
        _isExpanded: true,
        isNew: true // Флаг для нового дела
      };
      this.editableClient.legal_cases.forEach(c => c._isExpanded = false);
      this.editableClient.legal_cases.push(newCase);
      this.saveAllChanges();
    },
    addDocument(caseIndex) {
      this.editableClient.legal_cases[caseIndex].documents.push({
        document_type: '',
        status: 'NOT_SUBMITTED',
        files: [],
        isNew: true
      });
      // Сохранение произойдет при вводе названия и уходе с поля
    },
    removeDocument(caseIndex, docIndex) {
      this.confirmDialogMessage = 'Вы уверены, что хотите удалить эту строку?';
      this.confirmCallback = () => {
        this.editableClient.legal_cases[caseIndex].documents.splice(docIndex, 1);
        this.saveAllChanges();
      };
      this.showConfirmDialog = true;
    },
    removeCase(caseIndex) {
        this.confirmDialogMessage = 'Вы уверены, что хотите удалить это дело?';
        this.confirmCallback = () => {
            this.editableClient.legal_cases.splice(caseIndex, 1);
            this.saveAllChanges();
        };
        this.showConfirmDialog = true;
    },
    confirmAction() {
      if (this.confirmCallback) {
        this.confirmCallback();
      }
      this.cancelAction();
    },
    cancelAction() {
      this.showConfirmDialog = false;
      this.confirmDialogMessage = '';
      this.confirmCallback = null;
    },
    removeUploadedFile(legalCase, docIndex, fileIndex) {
      const file = this.editableClient.legal_cases[legalCase.id].documents[docIndex].files[fileIndex];
      // TODO: Добавить логику удаления файла с бэкенда, если нужно
      this.editableClient.legal_cases[legalCase.id].documents[docIndex].files.splice(fileIndex, 1);
      this.saveAllChanges();
    },
    triggerUpload(caseIndex, docIndex) {
      this.currentUploadInfo = { caseIndex, docIndex };
      // Используем уникальный ref
      const refName = `fileInput_${caseIndex}_${docIndex}`;
      const input = this.$refs[refName];
      if (input && input[0]) {
        input[0].click();
      } else {
        console.error('File input not found for', refName);
      }
    },
    async handleFileUpload(event) {
      const file = event.target.files[0];
      if (!file || !this.currentUploadInfo) return;

      const { caseIndex, docIndex } = this.currentUploadInfo;
      const legalCase = this.editableClient.legal_cases[caseIndex];
      const document = legalCase.documents[docIndex];

      const formData = new FormData();
      formData.append('file', file);
      formData.append('description', file.name); // или другое описание

      try {
        const token = localStorage.getItem('user-token');
        const response = await axios.post(
          `http://127.0.0.1:8000/api/documents/${document.id}/upload/`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
              'Authorization': `Token ${token}`
            }
          }
        );
        
        // Добавляем новый файл в список
        if (!document.files) {
          document.files = [];
        }
        document.files.push(response.data);

        this.showToast('Файл успешно загружен!', 'success');
      } catch (error) {
        console.error('Ошибка при загрузке файла:', error);
        this.showToast('Ошибка при загрузке файла.', 'error');
      } finally {
        // Сбрасываем значение инпута, чтобы можно было загрузить тот же файл снова
        event.target.value = '';
        this.currentUploadInfo = null;
      }
    },
    viewFile(file) {
      window.open(file.file, '_blank');
    },
    async saveAllChanges() {
        if (this.isSaving) return;
        this.isSaving = true;
        const token = localStorage.getItem('user-token');

        const payload = cloneDeep(this.editableClient);
        
        // Обрабатываем дела: новые добавляем, существующие обновляем
        payload.legal_cases.forEach(legalCase => {
            // Удаляем временные frontend-свойства
            delete legalCase._isExpanded;
            
            // Если дело новое, удаляем флаг isNew перед отправкой
            if (legalCase.isNew) {
                delete legalCase.isNew;
            }

            // Очищаем документы
            legalCase.documents = legalCase.documents
                .filter(doc => !(doc.isNew && !doc.document_type)) // Удаляем пустые новые документы
                .map(doc => {
                    const newDoc = { ...doc };
                    delete newDoc.isNew;
                    delete newDoc.files; 
                    return newDoc;
                });
        });

        try {
            // Отправляем PUT запрос с полным объектом клиента
            const response = await axios.put(`http://127.0.0.1:8000/api/clients/${this.id}/`, payload, {
                headers: { Authorization: `Token ${token}` }
            });
            
            // Сохраняем состояние раскрытых дел
            const expandedStates = new Map(
                this.editableClient.legal_cases.map((c, i) => [c.id || `new_${i}`, c._isExpanded])
            );

            // Обновляем данные и сбрасываем редактируемую копию
            this.client = response.data;
            this.resetEditableData();

            // Восстанавливаем состояние раскрытых дел
            this.editableClient.legal_cases.forEach((c, i) => {
                const key = c.id || `new_${i}`;
                if (expandedStates.has(key)) {
                    c._isExpanded = expandedStates.get(key);
                }
            });

            this.showToast('Сохранено!', 'success', 1500);

        } catch (error) {
            console.error("Ошибка сохранения:", error.response?.data || error);
            this.showToast('Не удалось сохранить данные.', 'error');
            // В случае ошибки, перезагружаем данные с сервера, чтобы откатить изменения
            await this.fetchClientData();
        } finally {
            this.isSaving = false;
        }
    },
    getStatusDisplay(statusKey) {
        return this.statusMap[statusKey] || statusKey;
    },
    getCaseTypeDisplay(caseTypeKey) {
        return this.caseTypeMap[caseTypeKey] || caseTypeKey || 'Новое дело';
    },
    getDocumentTypeDisplay(docKey) {
        return this.docTypeMap[docKey] || docKey;
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary-color: #4A9E80;
  --primary-hover-color: #428f74;
  --dark-blue: #2c3e50;
  --text-color: #5a6a7b;
  --background-color: #f7f9fc;
  --white-color: #ffffff;
  --input-border-color: #e0e6ed;
  --input-shadow: inset 0 1px 2px rgba(0,0,0,0.07);
  --border-color-light: #e0e6ed;
  --danger-color: #dc2626;
}

.client-card-wrapper {
  font-family: 'Inter', sans-serif;
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
  justify-content: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 6px;
  background-color: #ccd2da;
  color: var(--text-color);
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.2s ease;
  border: none;
  cursor: pointer;
}

.back-button:hover {
  background-color: #e0e6ed;
}

.back-button svg {
  width: 20px;
  height: 20px;
}

.card-header h1 {
  font-size: 22px;
  color: var(--dark-blue);
  margin: 0;
}

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
  align-items: end; /* Выравниваем элементы по нижнему краю */
}

.data-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  font-size: 15px;
  color: var(--dark-blue);
}

.data-item .value {
  font-size: 15px;
  padding: 12px 15px;
  background-color: var(--background-color);
  border-radius: 8px;
  height: 48px; /* Единая высота */
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
  height: 48px; /* ЕДИНАЯ ВЫСОТА ДЛЯ ВСЕХ */
  padding: 0 15px;
  border: 1px solid #ccd2da;
  border-radius: 8px;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
  font-size: 15px;
  background-color: var(--white-color);
  transition: border-color 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
}

.data-item textarea {
  padding: 12px 15px;
  resize: none;
}

.data-item :deep(.vti__input) {
  height: 100%;
  border: none;
  box-shadow: none;
  background-color: transparent;
  width: 100%;
  padding: 0;
}

.data-item :deep(.vti__dropdown) {
  padding: 0;
  display: flex;
  align-items: center;
}

.data-item :deep(.vue-tel-input.focus),
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

.cases-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.case-wrapper {
  border: 1px solid var(--border-color-light);
  border-radius: 10px;
  overflow: hidden;
  transition: box-shadow 0.2s ease;
}
.case-wrapper:hover {
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: var(--background-color);
  cursor: pointer;
}

.case-header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
  color: var(--dark-blue);
}
.case-header-title h4 {
  margin: 0;
}

.toggle-icon {
  width: 20px;
  height: 20px;
  color: #90a4ae;
  transition: transform 0.3s ease;
}
.toggle-icon.is-expanded {
  transform: rotate(90deg);
}

.case-details {
  padding: 20px;
  border-top: 1px solid var(--border-color-light);
}

.case-footer {
  padding-top: 20px;
  margin-top: 20px;
  border-top: 1px solid var(--border-color-light);
  display: flex;
  justify-content: flex-end;
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
  flex-wrap: wrap;
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
  flex-grow: 1;
  margin-right: 15px;
}
.doc-info input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  flex-shrink: 0;
}
.doc-name {
  font-size: 15px;
}
.other-doc-input {
  border: 1px solid var(--input-border-color);
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 15px;
  width: 100%;
}

.doc-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  flex-grow: 1;
  justify-content: flex-end;
}
.button-icon {
  padding: 8px;
  border-radius: 6px;
  border: 1px solid var(--input-border-color);
  background-color: #fff;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
  display: flex;
  align-items: center;
  justify-content: center;
}
.button-icon svg {
  width: 20px;
  height: 20px;
}
.button-icon.upload-doc {
  padding: 8px 16px;
}
.button-icon.upload-doc:hover {
  background-color: #eef2f7;
  color: var(--dark-blue);
  border-color: var(--dark-blue);
}
.button-icon.view-doc {
  color: #1e8e3e;
  border-color: #a8d8b6;
  padding: 8px 16px;
}
.button-icon.view-doc:hover {
  background-color: #e8f5e9;
}
.button-icon.delete-doc {
  color: var(--danger-color);
  border-color: #fecaca;
  padding: 8px 16px;
}
.button-icon.delete-doc:hover {
  background-color: #fee2e2;
}

.uploaded-files {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.file-chip {
  display: flex;
  align-items: center;
  background-color: #e8f5e9;
  color: #1e8e3e;
  border-radius: 16px;
  padding: 4px 6px 4px 12px;
  font-size: 14px;
  font-weight: 500;
}

.file-name {
  cursor: pointer;
  text-decoration: underline;
  margin-right: 6px;
}

.delete-file-btn {
  background: #b8ddc3;
  color: #1e8e3e;
  border: none;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}
.delete-file-btn:hover {
  background: #a8d8b6;
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
  border-radius: 12px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
}
.button.primary {
  background-color: var(--primary-color);
  color: var(--white-color);
  box-shadow: 0 6px 10px rgba(62, 63, 63, 0.25);
}
.button.primary:hover {
  background-color: var(--primary-hover-color);
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(62, 63, 63, 0.3);
}
.button.secondary {
  background-color: #f0f2f5;
  color: var(--dark-blue);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.05);
}
.button.secondary:hover {
  background-color: #e4e6e9;
  transform: translateY(-2px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.08);
}

.add-other-btn {
  margin-top: 15px;
  padding: 10px 20px;
  border-radius: 8px;
}

.card-footer {
  padding: 20px 30px;
  text-align: right;
  border-top: 1px solid var(--border-color-light);
  background-color: var(--background-color);
}

.confirm-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.confirm-dialog {
  background: white;
  padding: 30px 40px;
  border-radius: 12px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  text-align: center;
}

.confirm-dialog p {
  margin-bottom: 25px;
  font-size: 18px;
  color: var(--dark-blue);
  font-weight: 500;
}

.confirm-dialog-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
}

/* Toast Notification */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 25px;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  z-index: 2000;
  display: flex;
  align-items: center;
  gap: 10px;
}

.toast-notification.success {
  background-color: var(--primary-color);
}

.toast-notification.error {
  background-color: var(--danger-color);
}

.toast-fade-enter-active, .toast-fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}
.toast-fade-enter-from, .toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
