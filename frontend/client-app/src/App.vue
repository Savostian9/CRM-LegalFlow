<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
import { useToast } from 'vue-toastification'
import { useI18n } from 'vue-i18n'
import { onMounted, onUnmounted } from 'vue'

export default {
  setup() {
    const toast = useToast()
    const { t } = useI18n()

    const showRestricted = () => {
      toast.warning(t('billing.toast.restricted'))
    }

    onMounted(() => {
      window.addEventListener('show-restricted-toast', showRestricted)
    })

    onUnmounted(() => {
      window.removeEventListener('show-restricted-toast', showRestricted)
    })
  },
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

/* === Unified Page Title Styles === */
/* All dashboard pages should use these consistent styles */
/* Unified dashboard page paddings */
.content-wrapper,
.list-view-wrapper,
.page,
.finance-page,
.notifications-page,
.calendar-page,
.plan-page,
.faq-page,
.client-card-wrapper {
  padding: 24px 32px !important;
}

/* Unified dashboard headers */
.content-header,
.finance-header,
.page-header,
.cal-header,
.card-header,
.header {
  margin-bottom: 24px !important;
}

.content-header h1,
.finance-header h1,
.page-header h1,
.cal-header h1,
.cal-header h2,
.card-header h1,
.header h1,
.page-title,
.calendar-title {
  font-size: 28px !important;
  color: #2c3e50 !important;
  font-weight: 700 !important;
  margin: 0 !important;
}

/* (Form control styles centralized in styles/forms.css) */

/* Toast customization */
.Vue-Toastification__toast--warning {
  background-color: #fbbf24 !important; /* Amber-400 */
  color: #1f2937 !important; /* Dark gray text */
}
.Vue-Toastification__toast--warning .Vue-Toastification__close-button {
  color: #1f2937 !important;
  opacity: 0.7;
}
.Vue-Toastification__toast--warning .Vue-Toastification__icon {
  color: #1f2937 !important;
}
</style>