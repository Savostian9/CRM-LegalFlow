<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card">
      <header class="modal-header">
        <h2>Новый клиент</h2>
        <button @click="$emit('close')" class="close-button">&times;</button>
      </header>
      <form @submit.prevent="submitForm" class="modal-form">
        <div class="form-grid">
          <div class="form-group">
            <label for="first_name">Имя</label>
            <input type="text" id="first_name" v-model="clientData.first_name" required />
          </div>
          <div class="form-group">
            <label for="last_name">Фамилия</label>
            <input type="text" id="last_name" v-model="clientData.last_name" required />
          </div>
          <div class="form-group">
            <label for="email">Email</label>
            <input type="email" id="email" v-model="clientData.email" required />
          </div>
          <div class="form-group">
            <label for="phone_number">Телефон</label>
            <vue-tel-input v-model="clientData.phone_number" mode="international"></vue-tel-input>
          </div>
          <div class="form-group full-width">
            <label for="address">Адрес</label>
            <textarea id="address" v-model="clientData.address"></textarea>
          </div>
        </div>
        <footer class="modal-footer">
          <button type="button" @click="$emit('close')" class="button secondary">Отмена</button>
          <button type="submit" class="button primary">Сохранить</button>
        </footer>
      </form>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddClientModal',
  data() {
    return {
      clientData: {
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
        address: ''
      }
    };
  },
  methods: {
    submitForm() {
      // Отправляем данные родительскому компоненту
      this.$emit('save', this.clientData);
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
}
.modal-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 600px;
  overflow: hidden;
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
  width: 100%; padding: 10px; border: 1px solid #cdd4de; border-radius: 8px;
  box-sizing: border-box; /* Добавим на всякий случай */
}
.form-group textarea {
  min-height: 80px; resize: vertical;
}
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
.button.primary { background-color: #4A90E2; color: #fff; }
.button.secondary { background-color: #fff; border-color: #cdd4de; }
</style>