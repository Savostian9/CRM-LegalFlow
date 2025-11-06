<template>
  <div v-if="loading" class="loader">{{ $t('common.loading') }}</div>
  <div v-else-if="editableClient" class="client-card-wrapper">
    <header class="card-header">
      <div class="header-left">
  <button type="button" class="btn back-button" @click="goBack">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
            <path fill-rule="evenodd" d="M7.72 12.53a.75.75 0 0 1 0-1.06l7.5-7.5a.75.75 0 1 1 1.06 1.06L9.31 12l6.97 6.97a.75.75 0 1 1-1.06 1.06l-7.5-7.5Z" clip-rule="evenodd" />
          </svg>
          <span>{{ $t('clientDetail.back') }}</span>
		</button>
        <h1>{{ $t('clientDetail.title') }}: {{ editableClient.first_name }} {{ editableClient.last_name }}</h1>
      </div>
      <div class="header-actions">
        <button
          type="button"
          class="btn danger delete-client-btn"
          :disabled="pendingDelete"
          @click="promptDeleteClient"
          aria-label="Delete client"
        >
          <span class="btn-inner" v-if="!pendingDelete">
            <svg class="icon-trash" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M5 6l1 14a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-14"/></svg>
            {{ deleteClientLabel }}
          </span>
          <span v-else>{{ processingLabel }}</span>
        </button>
      </div>
    </header>

    <form @submit.prevent class="card-content">
      <section class="data-section">
        <h3>{{ $t('clientDetail.sections.personal') }}</h3>
        <div class="data-grid">
          <div class="data-item"><label>{{ $t('clientDetail.fields.firstName') }}</label><input type="text" v-model="editableClient.first_name" @change="saveAllChanges" /></div>
          <div class="data-item"><label>{{ $t('clientDetail.fields.lastName') }}</label><input type="text" v-model="editableClient.last_name" @change="saveAllChanges" /></div>
          <div class="data-item"><label>{{ $t('clientDetail.fields.phone') }}</label><vue-tel-input v-model="editableClient.phone_number" mode="international" @blur="saveAllChanges"></vue-tel-input></div>
          <div class="data-item"><label>{{ $t('clientDetail.fields.email') }}</label><input type="email" v-model="editableClient.email" @change="saveAllChanges" /></div>
          <div class="data-item full-width"><label>{{ $t('clientDetail.fields.address') }}</label><textarea v-model="editableClient.address" @change="saveAllChanges" class="address-textarea"></textarea></div>

          <div class="data-item"><label>{{ $t('clientDetail.fields.passportNumber') }}</label><input type="text" v-model="editableClient.passport_number" @change="saveAllChanges" /></div>
          <div class="data-item"><label>{{ $t('clientDetail.fields.passportExpiry') }}</label><AltDateTimePicker mode="date" v-model="editableClient.passport_expiry_date" @change="saveAllChanges" /></div>
          <div class="data-item"><label>{{ $t('clientDetail.fields.visaType') }}</label><input type="text" v-model="editableClient.visa_type" @change="saveAllChanges" /></div>
          <div class="data-item"><label>{{ $t('clientDetail.fields.visaExpiry') }}</label><AltDateTimePicker mode="date" v-model="editableClient.visa_expiry_date" @change="saveAllChanges" /></div>
        </div>
      </section>

      <section class="data-section">
  <h3>{{ $t('clientDetail.sections.reminders') }}</h3>
        <div class="data-grid">
          <div class="data-item" :class="{ 'has-error': reminderErrors.UMOWA_PRACA_ZLECENIA }">
            <label>{{ $t('clientDetail.reminders.UMOWA_PRACA_ZLECENIA') }}</label>
            <AltDateTimePicker mode="datetime" :min-now="true" v-model="remindersAtMap.UMOWA_PRACA_ZLECENIA" @close="onReminderAtChange('UMOWA_PRACA_ZLECENIA')" @invalid="() => onReminderInvalid('UMOWA_PRACA_ZLECENIA')" />
            <div class="field-msg">
              <small v-show="reminderErrors.UMOWA_PRACA_ZLECENIA" class="field-error">{{ reminderErrors.UMOWA_PRACA_ZLECENIA }}</small>
            </div>
          </div>
          <div class="data-item" :class="{ 'has-error': reminderErrors.UMOWA_NAJMU }">
            <label>{{ $t('clientDetail.reminders.UMOWA_NAJMU') }}</label>
            <AltDateTimePicker mode="datetime" :min-now="true" v-model="remindersAtMap.UMOWA_NAJMU" @close="onReminderAtChange('UMOWA_NAJMU')" @invalid="() => onReminderInvalid('UMOWA_NAJMU')" />
            <div class="field-msg">
              <small v-show="reminderErrors.UMOWA_NAJMU" class="field-error">{{ reminderErrors.UMOWA_NAJMU }}</small>
            </div>
          </div>
          <div class="data-item" :class="{ 'has-error': reminderErrors.ZUS_ZUA_ZZA }">
            <label>{{ $t('clientDetail.reminders.ZUS_ZUA_ZZA') }}</label>
            <AltDateTimePicker mode="datetime" :min-now="true" v-model="remindersAtMap.ZUS_ZUA_ZZA" @close="onReminderAtChange('ZUS_ZUA_ZZA')" @invalid="() => onReminderInvalid('ZUS_ZUA_ZZA')" />
            <div class="field-msg">
              <small v-show="reminderErrors.ZUS_ZUA_ZZA" class="field-error">{{ reminderErrors.ZUS_ZUA_ZZA }}</small>
            </div>
          </div>
          <div class="data-item" :class="{ 'has-error': reminderErrors.ZUS_RCA_DRA }">
            <label>{{ $t('clientDetail.reminders.ZUS_RCA_DRA') }}</label>
            <AltDateTimePicker mode="datetime" :min-now="true" v-model="remindersAtMap.ZUS_RCA_DRA" @close="onReminderAtChange('ZUS_RCA_DRA')" @invalid="() => onReminderInvalid('ZUS_RCA_DRA')" />
            <div class="field-msg">
              <small v-show="reminderErrors.ZUS_RCA_DRA" class="field-error">{{ reminderErrors.ZUS_RCA_DRA }}</small>
            </div>
          </div>
        </div>
      </section>

      <section class="data-section">
        <h3>{{ $t('clientDetail.sections.notes') }}</h3>
        <div class="notes-wrapper">
          <textarea
            v-model="editableClient.notes"
            class="notes-area"
            :placeholder="$t('clientDetail.notesPlaceholder')"
            @change="saveAllChanges"
          ></textarea>
        </div>
      </section>

      <section class="data-section">
  <h3>{{ $t('clientDetail.sections.finance') }}</h3>
        <div class="data-grid">
          <div class="data-item">
            <label>{{ $t('clientDetail.fields.serviceCost') }}</label>
            <input
              type="number"
              step="0.01"
              min="0"
              v-model.number="editableClient.service_cost"
              placeholder="0,00"
              @focus="clearIfZero('service_cost')"
              @blur="normalizeMoney('service_cost')"
            />
          </div>
          <div class="data-item">
            <label>{{ $t('clientDetail.fields.amountPaid') }}</label>
            <input
              type="number"
              step="0.01"
              min="0"
              v-model.number="editableClient.amount_paid"
              placeholder="0,00"
              @focus="clearIfZero('amount_paid')"
              @blur="normalizeMoney('amount_paid')"
            />
          </div>
          <div class="data-item">
            <label>{{ $t('clientDetail.fields.balance') }}</label>
            <input type="text" :value="formatCurrency(balanceComputed)" disabled />
          </div>
        </div>
      </section>

      <div v-if="!editableClient.legal_cases || editableClient.legal_cases.length === 0" class="empty-state">
        <p>{{ $t('clientDetail.cases.none') }}</p>
      </div>

      <div v-else class="cases-container">
        <div v-for="(legalCase, caseIndex) in editableClient.legal_cases" :key="legalCase.id || caseIndex" class="case-wrapper">
          <div class="case-header" @click="toggleCase(caseIndex)">
            <div class="case-header-title">
              <svg class="toggle-icon" :class="{ 'is-expanded': legalCase._isExpanded }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M7.21 14.77a.75.75 0 0 1 .02-1.06L11.168 10 7.23 6.29a.75.75 0 1 1 1.04-1.08l4.5 4.25a.75.75 0 0 1 0 1.08l-4.5 4.25a.75.75 0 0 1-1.06-.02Z" clip-rule="evenodd" />
              </svg>
              <h4>{{ $t('clientDetail.cases.caseN', { n: caseIndex + 1, type: getCaseTypeDisplay(legalCase.case_type) }) }}</h4>
            </div>
            <div class="case-status" :class="getCaseStatusClass(legalCase)">
              {{ getStatusDisplay(legalCase.status) }}
            </div>
          </div>

          <div v-if="legalCase._isExpanded" class="case-details">
            <section class="data-section">
              <h3>{{ $t('clientDetail.sections.caseData') }}</h3>
              <div class="data-grid">
                <div class="data-item full-width">
                  <label>{{ $t('clientDetail.cases.type') }}</label>
                  <select v-model="legalCase.case_type" @change="saveAllChanges">
                    <option value="-">-</option>
                    <option value="CZASOWY_POBYT">{{ $t('clientDetail.caseTypes.CZASOWY_POBYT') }}</option>
                    <option value="STALY_POBYT">{{ $t('clientDetail.caseTypes.STALY_POBYT') }}</option>
                    <option value="REZydent_UE">{{ $t('clientDetail.caseTypes.REZydent_UE') }}</option>
                    <option value="OBYWATELSTWO">{{ $t('clientDetail.caseTypes.OBYWATELSTWO') }}</option>
                  </select>
                </div>
                <div class="data-item"><label>{{ $t('clientDetail.cases.submissionDate') }}</label><AltDateTimePicker mode="date" v-model="legalCase.submission_date" @change="saveAllChanges" /></div>
                <div class="data-item"><label>{{ $t('clientDetail.cases.decisionDate') }}</label><AltDateTimePicker mode="date" v-model="legalCase.decision_date" @change="saveAllChanges" /></div>
                <div class="data-item full-width">
                  <label>{{ $t('clientDetail.cases.status') }}</label>
                  <select v-model="legalCase.status" @change="saveAllChanges">
                    <option value="-">-</option>
                    <option value="PREPARATION">{{ $t('clientDetail.caseStatus.PREPARATION') }}</option>
                    <option value="SUBMITTED">{{ $t('clientDetail.caseStatus.SUBMITTED') }}</option>
                    <option value="IN_PROGRESS">{{ $t('clientDetail.caseStatus.IN_PROGRESS') }}</option>
                    <option value="DECISION_POSITIVE">{{ $t('clientDetail.caseStatus.DECISION_POSITIVE') }}</option>
                    <option value="DECISION_NEGATIVE">{{ $t('clientDetail.caseStatus.DECISION_NEGATIVE') }}</option>
                    <option value="CLOSED">{{ $t('clientDetail.caseStatus.CLOSED') }}</option>
                  </select>
                </div>
              </div>
            </section>

            <section class="data-section">
              <h3>{{ $t('clientDetail.sections.checklist') }}</h3>
              <ul class="document-checklist">
                <li v-for="(doc, docIndex) in legalCase.documents" :key="doc.id || docIndex" class="document-item">
                  <div class="doc-info">
                    <input type="checkbox" v-model="doc.status" true-value="SUBMITTED" false-value="NOT_SUBMITTED" @change="saveAllChanges">
                    <input v-if="doc.isNew" type="text" v-model="doc.document_type" :placeholder="$t('clientDetail.cases.addDoc')" class="other-doc-input" @change="saveAllChanges">
                    <span v-else class="doc-name">{{ getDocumentTypeDisplay(doc.document_type) }}</span>
                  </div>
                  <div class="doc-actions">
                    <div v-if="doc.files && doc.files.length > 0" class="uploaded-files">
                      <div v-for="(file, fileIndex) in doc.files" :key="file.id || fileIndex" class="file-chip">
                        <span @click="viewFile(file)" class="file-name">{{ getFileDisplayName(file) }}</span>
                        <button type="button" @click="removeUploadedFile(caseIndex, docIndex, file)" class="delete-file-btn">&times;</button>
                      </div>
                    </div>
                    <button type="button" @click="triggerUpload(caseIndex, docIndex)" class="btn small upload-doc">{{ $t('clientDetail.cases.upload') }}</button>
                    <button
                      type="button"
                      @click="removeDocument(caseIndex, docIndex)"
                      class="btn danger small delete-doc icon-only"
                      :title="$t('clientDetail.cases.deleteRow')"
                      :aria-label="$t('clientDetail.cases.deleteRow')"
                    >
                      ×
                    </button>
                  </div>
                </li>
              </ul>
              <button type="button" @click="addDocument(caseIndex)" class="btn add-other-btn">{{ $t('clientDetail.cases.addDoc') }}</button>
              <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none;" multiple />
            </section>

            <footer class="case-footer">
              <button type="button" @click="removeCase(caseIndex)" class="btn danger small">{{ $t('clientDetail.cases.deleteCase') }}</button>
            </footer>
          </div>
        </div>
      </div>

      <footer class="card-footer">
        <div class="card-footer-left">
          <button
            type="button"
            class="btn danger delete-client-btn"
            :disabled="pendingDelete"
            @click="promptDeleteClient"
            aria-label="Delete client"
          >
            <span class="btn-inner" v-if="!pendingDelete">
              <svg class="icon-trash" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M5 6l1 14a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2l1-14"/></svg>
              {{ deleteClientLabel }}
            </span>
            <span v-else>{{ processingLabel }}</span>
          </button>
        </div>
        <div class="card-footer-right">
          <button type="button" @click="startNewCase" class="btn">{{ $t('clientDetail.cases.addNew') }}</button>
        </div>
      </footer>
    </form>

    <!-- Custom Confirm Dialog -->
    <div v-if="showConfirmDialog" class="confirm-dialog-overlay">
      <div class="confirm-dialog">
        <p>{{ confirmDialogMessage }}</p>
        <div class="confirm-dialog-actions">
          <button @click="confirmAction" class="btn danger">{{ $t('clientDetail.confirm.yesDelete') }}</button>
          <button @click="cancelAction" class="btn">{{ $t('clientDetail.confirm.cancel') }}</button>
        </div>
      </div>
    </div>

    <!-- Notification Toast -->
    <transition name="toast-fade">
      <div v-if="showNotification" :class="['toast-notification', notificationType]">
        {{ notificationMessage }}
      </div>
    </transition>
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
  remindersAtMap: { UMOWA_PRACA_ZLECENIA: null, UMOWA_NAJMU: null, ZUS_ZUA_ZZA: null, ZUS_RCA_DRA: null },
  reminderErrors: { UMOWA_PRACA_ZLECENIA: '', UMOWA_NAJMU: '', ZUS_ZUA_ZZA: '', ZUS_RCA_DRA: '' },
  reminderInvalidJustNow: { UMOWA_PRACA_ZLECENIA: false, UMOWA_NAJMU: false, ZUS_ZUA_ZZA: false, ZUS_RCA_DRA: false },
  statusMap: { '-' : '-', 'PREPARATION': this.$t('clientDetail.caseStatus.PREPARATION'), 'SUBMITTED': this.$t('clientDetail.caseStatus.SUBMITTED'), 'IN_PROGRESS': this.$t('clientDetail.caseStatus.IN_PROGRESS'), 'DECISION_POSITIVE': this.$t('clientDetail.caseStatus.DECISION_POSITIVE'), 'DECISION_NEGATIVE': this.$t('clientDetail.caseStatus.DECISION_NEGATIVE'), 'CLOSED': this.$t('clientDetail.caseStatus.CLOSED') },
  caseTypeMap: { '-' : '-', 'CZASOWY_POBYT': this.$t('clientDetail.caseTypes.CZASOWY_POBYT'), 'STALY_POBYT': this.$t('clientDetail.caseTypes.STALY_POBYT'), 'REZydent_UE': this.$t('clientDetail.caseTypes.REZydent_UE'), 'OBYWATELSTWO': this.$t('clientDetail.caseTypes.OBYWATELSTWO') },
  docTypeMap: { 'ZALACZNIK_1': this.$t('clientDetail.docTypes.ZALACZNIK_1'), 'UMOWA_PRACA': this.$t('clientDetail.docTypes.UMOWA_PRACA'), 'UMOWA_NAJMU': this.$t('clientDetail.docTypes.UMOWA_NAJMU'), 'ZUS_ZUA_ZZA': this.$t('clientDetail.docTypes.ZUS_ZUA_ZZA'), 'ZUS_RCA_DRA': this.$t('clientDetail.docTypes.ZUS_RCA_DRA'), 'POLISA': this.$t('clientDetail.docTypes.POLISA'), 'ZASWIADCZENIE_US': this.$t('clientDetail.docTypes.ZASWIADCZENIE_US'), 'ZASWIADCZENIA_ZUS': this.$t('clientDetail.docTypes.ZASWIADCZENIA_ZUS'), 'PIT_37': this.$t('clientDetail.docTypes.PIT_37'), 'BADANIE_LEKARSKIE': this.$t('clientDetail.docTypes.BADANIE_LEKARSKIE'), 'BADANIE_MEDYCZNE': this.$t('clientDetail.docTypes.BADANIE_MEDYCZNE'), 'SWIADECTWO_KIEROWCY': this.$t('clientDetail.docTypes.SWIADECTWO_KIEROWCY') },
      uploadingDocContext: null,
      showConfirmDialog: false,
      confirmDialogMessage: '',
      confirmCallback: null,
      showNotification: false,
      notificationMessage: '',
      notificationType: 'success',
      isSaving: false,
      pendingDelete: false,
    };
  },
  computed: {
    balanceComputed() {
      const cost = Number(this.editableClient?.service_cost || 0);
      const paid = Number(this.editableClient?.amount_paid || 0);
      return cost - paid;
    },
    deleteClientLabel() {
      const key = 'clientDetail.actions.deleteClient'
      const tr = this.$t(key)
        return tr === key ? 'Delete client' : tr
    },
    processingLabel() {
      const key = 'common.processing'
      const tr = this.$t(key)
        return tr === key ? 'Processing…' : tr
    }
  },
  created() {
    this.fetchClientData();
  },
  methods: {
    clearIfZero(field) {
      const val = Number(this.editableClient?.[field]);
      if (!val) {
        this.editableClient[field] = null; // очищаем поле при 0
      }
    },
    normalizeMoney(field) {
      let raw = this.editableClient?.[field];
      if (raw === '' || raw === null || raw === undefined || isNaN(Number(raw))) {
        raw = 0;
      }
      const num = Number(raw);
      // ограничим минимально 0 и округлим до 2 знаков
      const normalized = Math.max(0, Number(num.toFixed(2)));
      this.editableClient[field] = normalized;
      // сохраняем изменения после выхода из поля
      this.saveAllChanges();
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
  this.hydrateRemindersMap();
      } catch (error) {
        console.error("Ошибка при загрузке данных клиента:", error);
        this.showToast(this.$t('clientDetail.toasts.loadError'), 'error');
      } finally {
        this.loading = false;
      }
    },
    resetEditableData() {
        this.editableClient = cloneDeep(this.client);
        if (!this.editableClient.legal_cases) {
            this.editableClient.legal_cases = [];
        }
    if (!this.editableClient.reminders) {
      this.editableClient.reminders = [];
    }

        this.editableClient.legal_cases.forEach((legalCase) => {
            if (legalCase._isExpanded === undefined) {
                legalCase._isExpanded = false;
            }

            if (!legalCase.documents) {
                legalCase.documents = [];
            }

            const allDocTypes = Object.keys(this.docTypeMap);
            const existingDocsMap = new Map();
            
            legalCase.documents.forEach(doc => {
                existingDocsMap.set(doc.document_type, doc);
                if (!doc.files) doc.files = [];
            });

            const finalDocs = [];
            allDocTypes.forEach(docType => {
                if (existingDocsMap.has(docType)) {
                    finalDocs.push(existingDocsMap.get(docType));
                } else {
                    finalDocs.push({
                        document_type: docType,
                        status: 'NOT_SUBMITTED',
                        files: []
                    });
                }
            });

            legalCase.documents.forEach(doc => {
                if (!allDocTypes.includes(doc.document_type) && !finalDocs.find(d => d.document_type === doc.document_type)) {
                    finalDocs.push(doc);
                }
            });

            legalCase.documents = finalDocs;
        });
    },
    hydrateRemindersMap() {
      this.remindersAtMap = { UMOWA_PRACA_ZLECENIA: null, UMOWA_NAJMU: null, ZUS_ZUA_ZZA: null, ZUS_RCA_DRA: null };
      if (this.editableClient && Array.isArray(this.editableClient.reminders)) {
        for (const r of this.editableClient.reminders) {
          if (r.reminder_type === 'UMOWA_PRACA_ZLECENIA') {
            this.remindersAtMap.UMOWA_PRACA_ZLECENIA = this.combineDateTime(r.reminder_date, r.reminder_time);
          }
          if (r.reminder_type === 'UMOWA_NAJMU') {
            this.remindersAtMap.UMOWA_NAJMU = this.combineDateTime(r.reminder_date, r.reminder_time);
          }
          if (r.reminder_type === 'ZUS_ZUA_ZZA') {
            this.remindersAtMap.ZUS_ZUA_ZZA = this.combineDateTime(r.reminder_date, r.reminder_time);
          }
          if (r.reminder_type === 'ZUS_RCA_DRA') {
            this.remindersAtMap.ZUS_RCA_DRA = this.combineDateTime(r.reminder_date, r.reminder_time);
          }
        }
      }
    },
    onReminderAtChange(type) {
      if (!this.editableClient.reminders) this.editableClient.reminders = [];
      const idx = this.editableClient.reminders.findIndex(r => r.reminder_type === type);
      const picked = this.remindersAtMap[type];
      // Case 1: value became null
      if (!picked) {
        // If null right after invalid close, skip saving and consume the flag
        if (this.reminderInvalidJustNow[type]) {
          this.reminderInvalidJustNow[type] = false;
          return;
        }
        // User cleared the value explicitly: remove reminder if exists
        if (idx >= 0) {
          this.editableClient.reminders.splice(idx, 1);
          this.reminderErrors[type] = '';
          this.saveAllChanges();
        }
        return;
      }
      // Case 2: non-null picked; block past datetimes (minute precision)
      if (this.isPastDateTime(picked)) {
        // Reset UI model and set inline error, do not save
        this.remindersAtMap[type] = null;
        const eKey = 'clientDetail.errors.reminderPast';
        const eTr = this.$t(eKey);
        this.reminderErrors[type] = (eTr === eKey ? 'Нельзя выбрать прошедшие дату/время.' : eTr);
        this.reminderInvalidJustNow[type] = true;
        return;
      }
      // Valid value: clear errors and save
      if (this.reminderErrors[type]) this.reminderErrors[type] = '';
      this.reminderInvalidJustNow[type] = false;
      const parsed = this.splitDateTime(picked);
      const dateVal = parsed?.date || null;
      const timeVal = parsed?.time || null;
      if (idx >= 0) {
        this.editableClient.reminders[idx].reminder_date = dateVal;
        this.editableClient.reminders[idx].reminder_time = timeVal;
      } else {
        this.editableClient.reminders.push({ reminder_type: type, reminder_date: dateVal, reminder_time: timeVal });
      }
      this.saveAllChanges();
    },
    onReminderInvalid(type) {
      // Set inline error and mark invalid close; no toast so message persists under the field
      const eKey = 'clientDetail.errors.reminderPast';
      const eTr = this.$t(eKey);
      this.reminderErrors[type] = (eTr === eKey ? 'Нельзя выбрать прошедшие дату/время.' : eTr);
      this.reminderInvalidJustNow[type] = true;
    },
    isPastDateTime(dtLocal) {
      try {
        const [d, t = '00:00'] = String(dtLocal).split('T')
        const [Y, M, D] = d.split('-').map(n => Number(n))
        const [h, m] = t.split(':').map(n => Number(n))
        const picked = new Date(Y, (M || 1) - 1, D || 1, h || 0, m || 0, 0, 0)
        const now = new Date()
        const roundedNow = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), now.getMinutes(), 0, 0)
        return picked < roundedNow
      } catch { return false }
    },
    combineDateTime(dateStr, timeStr) {
      if (!dateStr) return null;
      const t = timeStr ? String(timeStr).slice(0,5) : '00:00';
      return `${dateStr}T${t}`;
    },
    splitDateTime(dtLocal) {
      if (!dtLocal) return null;
      try {
        const [datePart, timePart] = dtLocal.split('T');
        if (!datePart) return null;
        const time5 = (timePart || '00:00').slice(0,5);
        return { date: datePart, time: time5 };
      } catch { return null; }
    },
    startNewCase() {
      const newCase = {
        case_type: '-',
        submission_date: new Date().toISOString().slice(0, 10),
        decision_date: null,
        status: '-',
        documents: Object.keys(this.docTypeMap).map(key => ({
          document_type: key,
          status: 'NOT_SUBMITTED',
          files: []
        })),
        _isExpanded: false,
        isNew: true
      };
      
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
    },
    removeDocument(caseIndex, docIndex) {
  this.confirmDialogMessage = this.$t('clientDetail.confirm.deleteRow');
      this.confirmCallback = () => {
        this.editableClient.legal_cases[caseIndex].documents.splice(docIndex, 1);
        this.saveAllChanges();
      };
      this.showConfirmDialog = true;
    },
    removeCase(caseIndex) {
  this.confirmDialogMessage = this.$t('clientDetail.confirm.deleteCase');
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
    async removeUploadedFile(caseIndex, docIndex, file) {
      if (!file) return;
      // Серверный файл
      if (file.id) {
        const token = localStorage.getItem('user-token');
        try {
          await axios.delete(`http://127.0.0.1:8000/api/files/${file.id}/`, {
            headers: { Authorization: `Token ${token}` }
          });
          // Локально обновляем список файлов
          const doc = this.editableClient?.legal_cases?.[caseIndex]?.documents?.[docIndex];
          if (doc && Array.isArray(doc.files)) {
            doc.files = doc.files.filter(f => (f.id || null) !== file.id);
            if (doc.files.length === 0) doc.status = 'NOT_SUBMITTED';
          }
          this.showToast(this.$t('clientDetail.toasts.saved'), 'success', 900);
        } catch (e) {
          console.error('Delete file failed', e.response?.data || e);
          this.showToast(this.$t('clientDetail.toasts.saveError'), 'error');
        }
        return;
      }
      // Локально добавленный до сохранения
      const doc = this.editableClient?.legal_cases?.[caseIndex]?.documents?.[docIndex];
      if (!doc) return;
      const idx = (doc.files || []).indexOf(file);
      if (idx >= 0) doc.files.splice(idx, 1);
      if ((doc.files || []).length === 0) doc.status = 'NOT_SUBMITTED';
      // Не перезагружаем карточку
    },
    triggerUpload(caseIndex, docIndex) {
      this.uploadingDocContext = { caseIndex, docIndex };
      
      const fileInput = this.$refs.fileInput;
      if (Array.isArray(fileInput)) {
        if (fileInput.length > 0) {
          fileInput[0].click();
        }
      } else if (fileInput && typeof fileInput.click === 'function') {
        fileInput.click();
      } else {
        console.error('File input not found or click method not available');
      }
    },
    async handleFileUpload(event) {
      const files = event.target.files;
      if (!files.length || !this.uploadingDocContext) return;

      const { caseIndex, docIndex } = this.uploadingDocContext;
      const currentCase = this.editableClient?.legal_cases?.[caseIndex];
      if (!currentCase) { console.error('Case not found'); return; }
      const currentDoc = currentCase.documents?.[docIndex];
      if (!currentDoc) { console.error('Document not found'); return; }

      try {
        // Убедимся, что у документа есть ID в базе
        let docId = currentDoc.id;
        if (!docId) {
          await this.saveAllChanges();
          await this.fetchClientData();
          const refreshedCase = this.editableClient?.legal_cases?.[caseIndex];
          const match = refreshedCase?.documents?.find(d => d.document_type === currentDoc.document_type);
          if (match && match.id) {
            docId = match.id;
          }
        }
        if (!docId) {
          this.showToast(this.$t('clientDetail.toasts.saveError'), 'error');
          return;
        }

        // Загружаем одним запросом без полной перезагрузки карточки
        const token = localStorage.getItem('user-token');
        const fd = new FormData();
        for (const f of files) fd.append('files', f);
        try {
          const res = await axios.post(`http://127.0.0.1:8000/api/documents/${docId}/files/`, fd, {
            headers: { Authorization: `Token ${token}`, 'Content-Type': 'multipart/form-data' }
          });
          const payload = res?.data;
          const uploaded = Array.isArray(payload) ? payload : (payload ? [payload] : []);
          if (!Array.isArray(currentDoc.files)) currentDoc.files = [];
          uploaded.forEach(u => currentDoc.files.push(u));
          if (uploaded.length > 0) currentDoc.status = 'SUBMITTED';
          this.showToast(this.$t('clientDetail.toasts.saved'), 'success', 1200);
        } catch (e) {
          console.error('Upload failed', e.response?.data || e);
          this.showToast(this.$t('clientDetail.toasts.saveError'), 'error');
        }
      } finally {
        this.uploadingDocContext = null;
        if (event && event.target) event.target.value = '';
      }
    },
    viewFile(file) {
      const url = this.getFileUrl(file);
      if (url) window.open(url, '_blank');
    },
    getFileDisplayName(file) {
      if (!file) return '';
      if (file.name) return file.name;
      const url = file.file || file.url || '';
      if (!url) return '';
      try {
        const parts = url.split('?')[0].split('#')[0].split('/');
        return decodeURIComponent(parts[parts.length - 1] || 'file');
      } catch { return 'file'; }
    },
    getFileUrl(file) {
      if (!file) return '';
      if (file.url) return file.url;
      const f = file.file;
      if (!f) return '';
      if (/^https?:\/\//i.test(f)) return f;
      return `http://127.0.0.1:8000${f.startsWith('/') ? '' : '/'}${f}`;
    },
    async saveAllChanges() {
        if (this.isSaving) return;
        this.isSaving = true;
        const token = localStorage.getItem('user-token');

        const payload = cloneDeep(this.editableClient);
        
        const expandedStates = new Map();
        payload.legal_cases.forEach((legalCase, index) => {
            expandedStates.set(legalCase.id || `new_${index}`, legalCase._isExpanded);
        });

        payload.legal_cases = payload.legal_cases.map(legalCase => {
            const caseData = { ...legalCase };
            
            delete caseData._isExpanded;
            delete caseData.isNew;
            
            caseData.documents = caseData.documents
                .filter(doc => !(doc.isNew && !doc.document_type))
                .map(doc => {
                    const docData = { ...doc };
                    delete docData.isNew;
                    delete docData.files;
                    return docData;
                });
            
            return caseData;
        });

        // Ensure reminders array contains only necessary fields
        if (Array.isArray(payload.reminders)) {
          payload.reminders = payload.reminders.map(r => ({
            id: r.id,
            reminder_type: r.reminder_type,
            reminder_date: r.reminder_date,
            reminder_time: r.reminder_time,
            note: r.note
          }));
        }

        try {
            const response = await axios.put(`http://127.0.0.1:8000/api/clients/${this.id}/`, payload, {
                headers: { Authorization: `Token ${token}` }
            });
            
            this.client = response.data;
            
            if (this.editableClient.legal_cases) {
                this.editableClient.legal_cases.forEach((legalCase, index) => {
                    const key = legalCase.id || `new_${index}`;
                    if (expandedStates.has(key)) {
                        legalCase._isExpanded = expandedStates.get(key);
                    }
                });
            }
            
      this.showToast(this.$t('clientDetail.toasts.saved'), 'success', 1500);

        } catch (error) {
            console.error("Ошибка сохранения:", error.response?.data || error);
      this.showToast(this.$t('clientDetail.toasts.saveError'), 'error');
        } finally {
            this.isSaving = false;
        }
    },
          formatCurrency(val) {
            const num = Number(val || 0);
            try {
              const loc = (this.$i18n && this.$i18n.locale) || 'ru';
              const map = { ru: 'ru-RU', pl: 'pl-PL' };
              return num.toLocaleString(map[loc] || 'ru-RU', { style: 'currency', currency: 'PLN', minimumFractionDigits: 2 });
            } catch (e) {
              return `${num.toFixed(2)} PLN`;
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
    },
    promptDeleteClient() {
      const key = 'clientDetail.confirm.deleteClient'
      const tr = this.$t(key)
      this.confirmDialogMessage = (tr === key ? 'Delete this client? All related data will be removed.' : tr);
      this.confirmCallback = () => this.deleteClient();
      this.showConfirmDialog = true;
    },
    goBack(){
      // If there is a previous entry in history (length>1) just go back.
      // Some browsers keep initial length=1 for first page; fallback to clients list.
      try {
        if(window.history.length > 1){
          this.$router.back();
        } else {
          // Fallback to list
          this.$router.push('/dashboard/clients');
        }
      } catch(e){
        this.$router.push('/dashboard/clients');
      }
    },
    async deleteClient() {
      if (this.pendingDelete) return;
      this.pendingDelete = true;
      const token = localStorage.getItem('user-token');
      try {
        await axios.delete(`http://127.0.0.1:8000/api/clients/${this.id}/`, { headers: { Authorization: `Token ${token}` } });
        const keyOk = 'clientDetail.toasts.deleted'
        const okTr = this.$t(keyOk)
        this.showToast(okTr === keyOk ? 'Клиент удалён' : okTr, 'success');
        this.$router.push('/dashboard/clients');
      } catch (e) {
        console.error('Ошибка удаления клиента', e.response?.data || e);
        const keyErr = 'clientDetail.toasts.deleteError'
        const errTr = this.$t(keyErr)
        this.showToast(errTr === keyErr ? 'Ошибка удаления клиента' : errTr, 'error');
      } finally {
        this.pendingDelete = false;
      }
    }
  }
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
  --primary-color: #4A90E2; /* unify with sidebar blue */
  --primary-hover-color: #3b7fc9;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Unified notification-style buttons */
.btn { background: var(--btn-bg,#fff); border:1px solid var(--btn-border,#d0d7e2); padding:10px 18px; border-radius:8px; cursor:pointer; font-weight:600; font-size:14px; line-height:1.2; display:inline-flex; align-items:center; gap:8px; transition:background .25s, color .25s, border-color .25s, box-shadow .25s; color:#1e293b; }
.btn:hover { background: var(--primary-color,#4A90E2); color:#fff !important; border-color: var(--primary-color,#4A90E2); }
.btn:disabled { opacity:.55; cursor:not-allowed; }
.btn.small { padding:6px 12px; font-size:12px; }
.btn.danger { background:rgba(255,82,82,0.12); border:1px solid rgba(255,82,82,0.45); color:#c53030 !important; }
.btn.danger:hover { background:rgba(255,82,82,0.20); border-color:rgba(255,82,82,0.6); color:#a61b1b !important; }
.btn.danger:disabled { background:rgba(255,82,82,0.08); border-color:rgba(255,82,82,0.25); color:rgba(197,48,48,0.55) !important; }
.delete-client-btn .icon-trash { width:18px; height:18px; }
/* Icon-only variant */
.btn.icon-only { padding:6px; width:34px; height:34px; display:inline-flex; align-items:center; justify-content:center; font-size:20px; line-height:1; }
.btn.small.icon-only { padding:4px; width:28px; height:28px; font-size:18px; }
/* Old per-variant button styles removed; unified style above */

.header-left {
  display:flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
}

/* Old back-button styles removed (now uses .button palette) */

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
  width:100%;
  height:48px;
  padding:0 15px;
  border:1px solid var(--form-border,#e2e8f0);
  border-radius:8px;
  box-sizing:border-box;
  font-family:'Inter',sans-serif;
  font-size:15px;
  background:var(--form-bg,#fff);
  transition:border-color .18s ease, box-shadow .18s ease;
  display:flex; align-items:center;
}

.data-item textarea {
  padding: 12px 15px;
  resize: none;
}
.notes-wrapper { display:flex; flex-direction:column; width:100%; }
.notes-area { width:100%; max-width:100%; box-sizing:border-box; height:160px; padding:14px 16px; border:1px solid var(--form-border,#e2e8f0); border-radius:8px; resize:none; font-family:'Inter',sans-serif; line-height:1.4; font-size:14px; overflow-x:hidden; overflow-y:auto; background:var(--form-bg,#fff); transition:border-color .18s, box-shadow .18s; }
.notes-area:focus { outline:none; border-color:var(--form-border-focus,#4A9E80); box-shadow:var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18)); }

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
  outline:none;
  border-color:var(--form-border-focus,#4A9E80);
  box-shadow:var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18));
}

.data-item.full-width {
  grid-column: 1 / -1;
}

/* Inline field error styling for reminder pickers */
.data-item.has-error :deep(.mx-input) {
  border-color: var(--danger-color, #dc2626) !important;
  box-shadow: 0 0 0 2px rgba(220, 38, 38, 0.15) !important;
}
.field-error {
  display: block;
  /* no margin to avoid layout shift */
  margin: 0;
  color: var(--danger-color, #dc2626);
  font-size: 12px;
  line-height: 18px;
}
.field-msg { height: 18px; }

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

/* removed old .button base */

.add-other-btn {
  margin-top: 15px;
  padding: 10px 20px;
  border-radius: 8px;
}

.card-footer {
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border-color-light);
  background-color: var(--background-color);
}

.card-footer-left, .card-footer-right { display: flex; gap: 12px; }

/* Align delete client button (header & footer) */
.delete-client-btn { display:inline-flex; align-items:center; gap:8px; line-height:1; padding:10px 18px; }
.delete-client-btn .btn-inner { display:inline-flex; align-items:center; gap:8px; }
.delete-client-btn .icon-trash { width:18px; height:18px; display:block; }

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

/* Toast Notification (styled like buttons) */
.toast-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 10px;
  color: #fff;
  font-weight: 600;
  font-size: 14px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.18);
  z-index: 2000;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: linear-gradient(180deg,#4A90E2,#3b7fc9);
  border:1px solid #3b7fc9;
}
.toast-notification.success { /* inherits base blue styles */ --_success: 1; }
.toast-notification.error { background: linear-gradient(180deg,#dc2626,#b91c1c); border-color:#b91c1c; }

.toast-fade-enter-active, .toast-fade-leave-active {
  transition: opacity 0.5s, transform 0.5s;
}
.toast-fade-enter-from, .toast-fade-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
