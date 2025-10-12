<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
export default {
  components: { }
}
</script>

<style>
/* Глобальные переменные темы для всего приложения */
:root {
  /* Общие */
  --primary-color: #4A90E2;
  --bg: #f7f9fc;
  --text: #111827;
  --muted-text: #6b7280;
  --link-color: #2563eb;

  /* Поверхности/карточки/границы */
  --card-bg: #ffffff;
  --card-border: #e5e7eb;

  /* Кнопки/инпуты */
  --btn-bg: #ffffff;
  --btn-text: #111827;
  --btn-border: #ccd2da;
  --btn-primary-bg: var(--primary-color);
  --btn-primary-text: #ffffff;

  --input-bg: #ffffff;
  --input-border: #e0e6ed;
}

[data-theme="dark"] {
  --primary-color: #4A90E2;
  --bg: #0f172a;            /* фон контента */
  --text: #e5e7eb;
  --muted-text: #cbd5e1;
  --link-color: #93c5fd;

  --card-bg: #111827;       /* карточки/поверхности */
  --card-border: #23304a;   /* границы */

  --btn-bg: #0b1220;        /* фон нейтральных кнопок */
  --btn-text: #e5e7eb;
  --btn-border: #24344d;
  --btn-primary-bg: var(--primary-color);
  --btn-primary-text: #ffffff;

  --input-bg: #0b1220;
  --input-border: #24344d;
}

/* Базовые стили */
html, body, #app { height: 100%; }
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: var(--bg);
  color: var(--text);
}
a { color: var(--link-color); }

/* (Form control styles centralized in styles/forms.css) */
</style>