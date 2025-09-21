<template>
  <div class="content-wrapper">
    <header class="content-header">
      <h1>Главная</h1>
    </header>
    <div class="content-body">
      <div class="welcome-card">
        <h2>Добро пожаловать!</h2>
        <p>Это ваша отправная точка. Здесь будет сводка по всем вашим делам, документам и предстоящим задачам.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardHomeView'
}
</script>

<style scoped>
/* Стили только для этой конкретной страницы */
.content-wrapper {
  padding: 40px;
}
.content-header {
  margin-bottom: 30px;
}
.content-header h1 {
  font-size: 28px;
  color: #2c3e50;
  font-weight: 700;
}
.welcome-card {
  background-color: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.05);
}
.welcome-card h2 {
  font-size: 24px;
  color: #2c3e50;
  margin-top: 0;
}
</style>