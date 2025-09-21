<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <header class="modal-header">
        <h2>Новое дело</h2>
        <button @click="$emit('close')" class="close-button">&times;</button>
      </header>
      <form @submit.prevent="submitForm" class="modal-form">
        <div class="form-group">
          <label for="submission_date">Дата подачи</label>
          <input type="date" id="submission_date" v-model="caseData.submission_date" required />
        </div>
        <div class="form-group">
          <label for="status">Статус</label>
          <select id="status" v-model="caseData.status">
            <option value="PREPARATION">Подготовка документов</option>
            <option value="SUBMITTED">Подано</option>
            <option value="IN_PROGRESS">На рассмотрении</option>
          </select>
        </div>
        <footer class="modal-footer">
          <button type="button" @click="$emit('close')" class="button secondary">Отмена</button>
          <button type="submit" class="button primary">Создать дело</button>
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
/* Стили здесь похожи на AddClientModal */
.modal-overlay { /* ... */ }
.modal-card { /* ... */ }
/* ... и так далее, можете скопировать стили из AddClientModal.vue */
.form-group input, .form-group select {
  width: 100%; padding: 10px; border: 1px solid #cdd4de; border-radius: 8px;
}
.modal-footer, .modal-header, .button { /* ... */ }
</style>