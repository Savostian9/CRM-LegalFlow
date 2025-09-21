<template>
  <div class="home-container">
    <header class="header">
      <div class="logo">
        <router-link to="/">LegalFlow</router-link>
      </div>
      <nav class="auth-buttons">
        <router-link to="/login" class="button secondary">Войти</router-link>
        <router-link to="/register" class="button primary">Начать работу</router-link>
      </nav>
    </header>

    <main class="hero-section">
      <div class="hero-content">
        <h1 class="hero-headline">
          Автоматизируйте легализацию.<br> Управляйте бизнесом легко.
        </h1>
        <p class="hero-subheadline">
          Наша CRM — это единая платформа для безупречной работы с клиентами по визам, TRC и картам побыту. Увеличьте продуктивность вашей команды уже сегодня.
        </p>
        <router-link to="/register" class="button primary cta-button">Попробовать бесплатно</router-link>
      </div>
      <div class="hero-graphic">
        <div class="graphic-element"></div>
        <div class="graphic-element small"></div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
/* Импорт современного шрифта */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* Анимация появления */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:root {
  --primary-color: #4A90E2;
  --primary-hover: #357ABD;
  --dark-blue: #2c3e50;
  --text-color: #5a6a7b;
  --background-color: #f7f9fc;
  --white-color: #ffffff;
  --border-color: #e0e6ed;
}

.home-container {
  font-family: 'Inter', sans-serif;
  background-color: var(--white-color);
  color: var(--text-color);
  min-height: 100vh;
  overflow-x: hidden; /* Предотвращаем горизонтальный скролл */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 60px;
  border-bottom: 1px solid var(--border-color);
}

.logo a {
  font-size: 26px;
  font-weight: 700;
  text-decoration: none;
  color: var(--dark-blue);
}

.auth-buttons {
  display: flex;
  gap: 15px;
}

.button {
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  white-space: nowrap; /* Запрещаем перенос текста на кнопках */
}

.button.primary {
  background-color: var(--primary-color);
  color: var(--white-color);
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.2);
}

.button.primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(74, 144, 226, 0.3);
}

.button.secondary {
  background-color: #f0f2f5;
  color: var(--dark-blue);
  border-color: transparent;
}

.button.secondary:hover {
  background-color: #e4e6e9;
  color: var(--dark-blue);
}

.hero-section {
  display: grid;
  grid-template-columns: 1fr 0.8fr;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 60px;
  gap: 40px;
}

.hero-content {
  animation: fadeInUp 0.8s ease-out;
}

.hero-headline {
  font-size: 3.2em;
  font-weight: 700;
  color: var(--dark-blue);
  line-height: 1.2;
  margin-bottom: 25px;
}

.hero-subheadline {
  font-size: 1.15em;
  line-height: 1.7;
  max-width: 500px;
  margin-bottom: 40px;
}

.cta-button {
  font-size: 1.1em;
  padding: 18px 36px;
}

.hero-graphic {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeInUp 0.8s ease-out 0.2s;
  animation-fill-mode: backwards;
}

.graphic-element {
  background: linear-gradient(45deg, var(--primary-color), #81c784);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
  position: relative;
}

.graphic-element:not(.small) {
  width: 300px;
  height: 400px;
  transform: rotate(-15deg);
}

.graphic-element.small {
  width: 150px;
  height: 250px;
  position: absolute;
  bottom: -40px;
  right: 20px;
  transform: rotate(10deg);
  background: linear-gradient(45deg, #ffb74d, #f06292);
}

/* --- НАЧАЛО АДАПТИВНОСТИ --- */

/* Планшеты (до 992px) */
@media (max-width: 992px) {
  .header {
    padding: 20px 40px;
  }

  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 60px 40px;
  }

  .hero-graphic {
    display: none; /* Скрываем графику на планшетах и телефонах */
  }

  .hero-subheadline {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-headline {
    font-size: 2.8em; /* Немного уменьшаем заголовок */
  }
}

/* Телефоны (до 576px) */
@media (max-width: 576px) {
  .header {
    padding: 15px 20px;
  }

  .logo a {
    font-size: 22px; /* Уменьшаем логотип */
  }
  
  .button {
    padding: 10px 16px; /* Уменьшаем кнопки */
    font-size: 0.9em;
  }

  .hero-section {
    padding: 40px 20px;
  }

  .hero-headline {
    font-size: 2.2em; /* Значительно уменьшаем заголовок */
  }

  .hero-subheadline {
    font-size: 1em;
  }

  .cta-button {
    font-size: 1em;
    padding: 15px 30px;
  }
}
/* --- КОНЕЦ АДАПТИВНОСТИ --- */
</style>