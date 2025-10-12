<template>
  <div class="lang-widget" role="group" aria-label="Language switcher">
    <button
      :class="['lang-btn', { active: current === 'pl' }]"
      @click="change('pl')"
      title="Polski"
      aria-label="Polski"
    >🇵🇱 <span class="code">PL</span></button>
    <button
      :class="['lang-btn', { active: current === 'ru' }]"
      @click="change('ru')"
      title="Русский"
      aria-label="Русский"
    >🇷🇺 <span class="code">RU</span></button>
  </div>
</template>

<script>
export default {
  name: 'LangSwitcher',
  computed: {
    current() { return this.$i18n.locale; }
  },
  methods: {
    change(locale) {
      try {
        if (this.$i18n.locale === locale) return;
        this.$i18n.locale = locale;
        localStorage.setItem('locale', locale);
        document.documentElement.setAttribute('lang', locale);
      } catch (e) {
        // no-op
      }
    }
  }
}
</script>

<style scoped>
.lang-widget {
  display: inline-flex;
  gap: 6px;
  padding: 6px;
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(0,0,0,0.08);
  border-radius: 999px;
  backdrop-filter: blur(6px);
  box-shadow: 0 4px 14px rgba(0,0,0,0.1);
}
.lang-btn {
  appearance: none;
  border: 0;
  background: transparent;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  color: #1f2937;
}
.lang-btn .code { font-size: 12px; opacity: 0.8; }
.lang-btn.active { background: var(--primary-color); color: #fff; }
[data-theme="dark"] .lang-widget { background: rgba(17,24,39,0.8); border-color: rgba(255,255,255,0.08); }
[data-theme="dark"] .lang-btn { color: #e5e7eb; }
</style>
