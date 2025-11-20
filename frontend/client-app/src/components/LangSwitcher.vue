
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
  gap: 8px;
  padding: 8px 14px;
  background: linear-gradient(90deg, #e3eafc 0%, #f7f9fc 100%);
  border: 1px solid #e0e6ed;
  border-radius: 999px;
  backdrop-filter: blur(8px);
  box-shadow: 0 6px 24px rgba(74,144,226,0.10);
  transition: box-shadow 0.22s, background 0.22s;
}
.lang-btn {
  appearance: none;
  border: 0;
  background: transparent;
  padding: 8px 18px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 1em;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  cursor: pointer;
  color: #1f2937;
  transition: background 0.18s, color 0.18s, box-shadow 0.18s, transform 0.18s;
  position: relative;
}
.lang-btn .code { font-size: 13px; opacity: 0.8; }
.lang-btn.active {
  background: linear-gradient(90deg, #2563eb 0%, #4A90E2 100%);
  color: #fff;
  box-shadow: 0 4px 18px rgba(74,144,226,0.18);
  z-index: 1;
  transform: scale(1.08);
}
.lang-btn:not(.active):hover, .lang-btn:not(.active):focus {
  background: #e0e6ed;
  color: #2563eb;
  box-shadow: 0 2px 8px rgba(74,144,226,0.10);
  transform: scale(1.04);
}
[data-theme="dark"] .lang-widget { background: rgba(17,24,39,0.8); border-color: rgba(255,255,255,0.08); }
[data-theme="dark"] .lang-btn { color: #e5e7eb; }
</style>
