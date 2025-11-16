<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <header class="modal-header">
  <h2>{{ $t('modals.addClient.title') }}</h2>
        <button @click="$emit('close')" class="close-button">&times;</button>
      </header>
      <form @submit.prevent="submitForm" class="modal-form">
        <div class="form-grid">
          <div class="form-group">
            <label for="first_name">{{ $t('common.firstName') }}</label>
            <input type="text" id="first_name" v-model="clientData.first_name" required />
          </div>
          <div class="form-group">
            <label for="last_name">{{ $t('common.lastName') }}</label>
            <input type="text" id="last_name" v-model="clientData.last_name" required />
          </div>
          <div class="form-group">
            <label for="email">{{ $t('common.email') }}</label>
            <input type="email" id="email" v-model="clientData.email" required />
          </div>
          <div class="form-group">
            <label for="phone_number">{{ $t('common.phone') }}</label>
            <vue-tel-input v-model="clientData.phone_number" mode="international"></vue-tel-input>
          </div>
          
          <div v-if="canChooseManager" class="form-group full-width">
            <label for="responsible_manager">{{ $t('modals.addClient.manager') }}</label>
            <UiSelect
              v-model="selectedManagerId"
              :options="[{ value: '', label: '— ' + ($t('modals.addClient.chooseManager') || 'Выберите менеджера') + ' —' }, ...managers.map(m => ({ value: String(m.id), label: m.name }))]"
              :placeholder="$t('modals.addClient.chooseManager')"
              :aria-label="$t('modals.addClient.manager')"
            />
            <small class="hint">{{ $t('modals.addClient.managerHint') }}</small>
          </div>
          
        </div>
        <footer class="modal-footer">
          <button type="button" @click="$emit('close')" class="button secondary">{{ $t('common.cancel') }}</button>
          <button type="submit" class="button primary">{{ $t('common.save') }}</button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script>
import UiSelect from './UiSelect.vue';
export default {
  name: 'AddClientModal',
  components: { UiSelect },
  props: {
    canChooseManager: { type: Boolean, default: false },
    managers: { type: Array, default: () => [] }
  },
  data() {
    return {
      clientData: {
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
      },
      selectedManagerId: ''
    };
  },
  methods: {
    submitForm() {
      // Отправляем данные родительскому компоненту
      const payload = { ...this.clientData };
      if (this.canChooseManager && this.selectedManagerId) {
        payload.responsible_manager_id = this.selectedManagerId;
      }
      this.$emit('save', payload);
    }
  }
};
</script>

<style scoped>
/* Стили для модального окна */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  /* Разрешаем вложенным выпадающим спискам выходить за пределы overlay */
  overflow: visible;
}
.modal-card {
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 600px;
  /* Нужно, чтобы список стран (vue-tel-input) не обрезался */
  overflow: visible;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e0e6ed;
}
.modal-header h2 {
  margin: 0; font-size: 20px;
}
.close-button {
  background: none; border: none; font-size: 28px; cursor: pointer; color: #90a4ae;
}
.modal-form {
  padding: 25px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  /* --- ЭТА СТРОКА ВСЁ ИСПРАВИТ --- */
  align-items: start; 
}
.form-group.full-width {
  grid-column: 1 / -1;
}
.form-group label {
  display: block; margin-bottom: 8px; font-weight: 500;
}
.form-group input, .form-group textarea {
  width: 100%; padding: 10px; border: 1px solid var(--form-border,#e2e8f0); border-radius: var(--form-radius,8px);
  box-sizing: border-box; background:var(--form-bg,#fff); font-size:14px; transition:border-color .18s, box-shadow .18s, background-color .25s;
}
.form-group input:focus, .form-group textarea:focus, .form-group select:focus, .form-group :deep(input[type='tel']:focus) {
  outline:none; border-color:var(--form-border-focus,#4A9E80); box-shadow:var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18));
}
.form-group textarea {
  min-height: 80px; resize: vertical;
}
.form-group select {
  width: 100%; padding: 10px; border: 1px solid var(--form-border,#e2e8f0); border-radius: var(--form-radius,8px); box-sizing: border-box; background:var(--form-bg,#fff); transition:border-color .18s, box-shadow .18s;
}
/* vue-tel-input adjustment to inherit unified styles */
:deep(.vue-tel-input) { --vti-border-color: var(--form-border,#e2e8f0); border:1px solid var(--form-border,#e2e8f0); border-radius:var(--form-radius,8px); background:var(--form-bg,#fff); padding:0 0 0 4px; }
:deep(.vue-tel-input:focus-within) { border-color:var(--form-border-focus,#4A9E80); box-shadow:var(--form-focus-ring,0 0 0 2px rgba(74,158,128,.18)); }
:deep(.vue-tel-input .vti__input) { font-family:inherit; font-size:14px; padding:8px 10px; }
/* Remove inner borders to avoid double outline */
:deep(.vue-tel-input input) { border:none !important; box-shadow:none !important; outline:none !important; background:transparent; }
/* Country dropdown separator subtle */
:deep(.vue-tel-input .vti__dropdown) { border:none; border-right:1px solid var(--form-border,#e2e8f0); background:transparent; }
:deep(.vue-tel-input .vti__dropdown.open) { background:#f1f5f9; }
/* Список стран поверх модалки */
:deep(.vue-tel-input .vti__dropdown-list) {
  z-index: 1101;
  max-height: 300px;
  overflow: auto;
  margin-top: 6px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
  border-radius: 8px;
  border: 1px solid var(--form-border,#e2e8f0);
  background: var(--form-bg,#fff);
}
.hint { display: block; color: #6b7280; font-size: 12px; margin-top: 6px; }
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 25px;
  border-top: 1px solid #e0e6ed;
  background-color: #f7f9fc;
}
.button {
  padding: 10px 20px; border-radius: 8px; font-weight: 600; border: 1px solid transparent; cursor: pointer;
}
.button.primary { background-color: var(--primary-color); color: #fff; }
.button.secondary { background-color: var(--btn-bg); color: var(--btn-text); border-color: var(--btn-border); }
</style>