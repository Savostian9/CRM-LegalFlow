<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <header class="modal-header">
  <h2>{{ $t('modals.addCase.title') }}</h2>
        <button @click="$emit('close')" class="close-button">&times;</button>
      </header>
      <form @submit.prevent="submitForm" class="modal-form">
        <div class="form-group">
          <label for="submission_date">{{ $t('modals.addCase.submissionDate') }}</label>
          <input type="date" id="submission_date" v-model="caseData.submission_date" required />
        </div>
        <div class="form-group">
          <label for="status">{{ $t('modals.addCase.status') }}</label>
          <select id="status" v-model="caseData.status">
            <option value="PREPARATION">{{ $t('case.status.preparation') }}</option>
            <option value="SUBMITTED">{{ $t('case.status.submitted') }}</option>
            <option value="IN_PROGRESS">{{ $t('case.status.inProgress') }}</option>
          </select>
        </div>
        <footer class="modal-footer">
          <button type="button" @click="$emit('close')" class="button secondary">{{ $t('common.cancel') }}</button>
          <button type="submit" class="button primary">{{ $t('modals.addCase.create') }}</button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddCaseModal',
  data() {
    return {
      caseData: {
        submission_date: new Date().toISOString().slice(0, 10), // Сегодняшняя дата по умолчанию
        status: 'PREPARATION',
      }
    };
  },
  methods: {
    submitForm() {
      this.$emit('save', this.caseData);
    }
  }
};
</script>

<style scoped>
/* Стили модального окна — приведены к тем же, что и AddClientModal */
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
}
.modal-card {
  background: var(--card-bg);
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 540px;
  overflow: hidden;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #e0e6ed;
}
.modal-header h2 { margin: 0; font-size: 20px; }
.close-button { background: none; border: none; font-size: 28px; cursor: pointer; color: #90a4ae; }
.modal-form { padding: 25px; }
.form-group { margin-bottom: 16px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; }
.form-group input, .form-group select {
  width: 100%; padding: 10px; border: 1px solid #cdd4de; border-radius: 8px; box-sizing: border-box;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 25px;
  border-top: 1px solid #e0e6ed;
  background-color: #f7f9fc;
}
.button { padding: 10px 20px; border-radius: 8px; font-weight: 600; border: 1px solid transparent; cursor: pointer; }
.button.primary { background-color: var(--primary-color); color: #fff; }
.button.secondary { background-color: var(--btn-bg); color: var(--btn-text); border-color: var(--btn-border); }
</style>