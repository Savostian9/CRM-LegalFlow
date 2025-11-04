<template>
  <div class="page faq-page">
    <header class="page-header">
      <h1>{{ $t('faq.title') || 'FAQ — Частые вопросы' }}</h1>
      <p class="lead">{{ $t('faq.lead') }}</p>
    </header>

  <section class="faq-list" aria-label="FAQ">
      <details v-for="(item, idx) in faqs" :key="idx" :id="item.anchor">
        <summary>
          <span class="q">{{ item.q }}</span>
        </summary>
        <div class="a" v-html="item.a"></div>
      </details>
    </section>

    <footer class="faq-footer">
      <p>
        {{ $t('faq.footer') }}
        <a href="mailto:crmlegalflow@gmail.com">crmlegalflow@gmail.com</a>
      </p>
    </footer>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

const { tm } = useI18n()
const faqs = computed(() => {
  const items = tm('faq.items')
  return Array.isArray(items) ? items : []
})
</script>

<style scoped>
.page { padding: 24px; }
.page-header { margin-bottom: 18px; }
.page-header h1 { font-size: 24px; margin: 0 0 6px; }
.page-header .lead { color: #475569; margin: 0; }

.faq-list { display: grid; gap: 10px; }
.faq-list details { background: var(--card-bg, #fff); border: 1px solid var(--card-border, #e5e7eb); border-radius: 10px; padding: 10px 14px; }
.faq-list summary { cursor: pointer; font-weight: 600; color: #0f172a; outline: none; }
.faq-list summary::-webkit-details-marker { display:none; }
.faq-list summary { display:flex; align-items:center; gap:8px; }
.faq-list summary::before { content:'❓'; opacity:.8; }
.faq-list .a { color:#334155; padding:10px 2px 2px; line-height: 1.5; }
.faq-list a { color: var(--primary-color, #4A90E2); text-decoration: none; }
.faq-list a:hover { text-decoration: underline; }

.faq-footer { margin-top: 16px; color: #475569; }
</style>
