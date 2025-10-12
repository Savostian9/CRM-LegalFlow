<template>
  <div class="pricing-wrapper">
    <h3 class="pricing-title">Тарифы</h3>
    <div class="pricing-grid">
      <div
        v-for="plan in plans"
        :key="plan.code"
        class="plan-card"
        :class="plan.code.toLowerCase()"
      >
        <div class="plan-head">
          <h4>{{ plan.name }}</h4>
          <span v-if="plan.badge" class="badge" :class="{ primary: plan.highlight }">{{ plan.badge }}</span>
        </div>
        <div class="price">
          <template v-if="plan.price === 0">0 PLN <span>/ {{ plan.pricePeriod }}</span></template>
          <template v-else>{{ plan.price }} PLN <span>/ {{ plan.pricePeriod }}</span></template>
        </div>
        <p class="desc">{{ plan.description }}</p>
        <ul class="features">
          <li v-for="f in plan.features" :key="f">{{ f }}</li>
        </ul>
        <!-- Детали всегда показаны -->
        <div class="details">
          <h5>Что входит</h5>
          <table class="limits-table">
            <tbody>
              <tr>
                <td>Пользователи</td>
                <td>{{ plan.limits.users }}</td>
              </tr>
              <tr>
                <td>Клиенты</td>
                <td>{{ plan.limits.clients }}</td>
              </tr>
              <tr>
                <td>Дела</td>
                <td>{{ plan.limits.cases }}</td>
              </tr>
              <tr>
                <td>Файлы</td>
                <td>{{ plan.limits.files }}</td>
              </tr>
              <tr>
                <td>Хранилище</td>
                <td>{{ formatStorage(plan.limits.files_storage_mb) }}</td>
              </tr>
              <tr>
                <td>Задачи / месяц</td>
                <td>{{ plan.limits.tasks_per_month }}</td>
              </tr>
              <tr>
                <td>Активные напоминания</td>
                <td>{{ plan.limits.reminders_active }}</td>
              </tr>
              <tr>
                <td>Email / месяц</td>
                <td>{{ plan.limits.emails_per_month }}</td>
              </tr>
            </tbody>
          </table>
          <div class="qualitative" v-if="plan.qualitative?.length">
            <h5>Дополнительно</h5>
            <ul class="qual-list">
              <li v-for="q in plan.qualitative" :key="q.key">{{ q.label }}: <strong>{{ q.value }}</strong></li>
            </ul>
          </div>
        </div>
        <div class="actions">
          <button
            v-if="plan.code !== 'TRIAL'"
            class="upgrade-btn"
            @click="$emit('select', plan.code)"
          >
            Выбрать
          </button>
          <div v-else class="cta muted">Активируется при регистрации</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getPlanCatalogArray, formatStorage } from '../billing/planCatalog';
export default {
  name: 'PricingPlans',
  props: { showTrial: { type: Boolean, default: true } },
  computed: {
    plans() {
      const all = getPlanCatalogArray();
      return this.showTrial ? all : all.filter(p => p.code !== 'TRIAL');
    }
  },
  methods: {
    formatStorage(mb) { return formatStorage(mb); }
  }
}
</script>

<style scoped>
.pricing-wrapper { margin-top: 40px; }
.pricing-title { text-align:center; font-weight:600; margin-bottom:18px; color:#2c3e50; }
.pricing-grid { display:grid; gap:24px; grid-template-columns: repeat(auto-fit,minmax(260px,1fr)); }
.plan-card { background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:20px 20px 24px; position:relative; display:flex; flex-direction:column; box-shadow:0 4px 12px rgba(0,0,0,0.04); }
.plan-card.trial { border-color:#94a3b8; }
.plan-card.starter { border-color:#3b82f6; }
.plan-card.pro { border-color:#9333ea; }
.plan-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
.plan-head h4 { font-size:18px; margin:0; font-weight:600; }
.badge { background:#e2e8f0; color:#334155; font-size:11px; padding:4px 8px; border-radius:20px; font-weight:500; }
.badge.primary { background:#2563eb; color:#fff; }
.price { font-size:26px; font-weight:700; margin:10px 0 8px; }
.price span { font-size:13px; font-weight:400; color:#64748b; }
.desc { font-size:13px; color:#64748b; margin:0 0 12px; line-height:1.35; }
.features { list-style:none; padding:0; margin:0 0 10px; font-size:13px; color:#374151; display:flex; flex-direction:column; gap:4px; }
.features li { position:relative; padding-left:16px; }
.features li:before { content:'✔'; position:absolute; left:0; top:0; color:#16a34a; font-size:11px; line-height:1.2; }
.details { margin:8px 0 10px; border-top:1px dashed #e2e8f0; padding-top:10px; }
.limits-table { width:100%; border-collapse:collapse; font-size:12px; margin-bottom:8px; }
.limits-table td { padding:4px 4px; border-bottom:1px solid #f1f5f9; }
.limits-table tr:last-child td { border-bottom:none; }
.qualitative { margin-top:6px; }
.qualitative h5 { font-size:12px; margin:0 0 4px; text-transform:uppercase; letter-spacing:.5px; color:#475569; }
.qual-list { list-style:none; padding:0; margin:0; font-size:12px; display:flex; flex-direction:column; gap:4px; }
.actions { margin-top:auto; display:flex; flex-direction:column; gap:8px; }
.upgrade-btn { background:linear-gradient(90deg,#2563eb,#1d4ed8); color:#fff; border:none; border-radius:8px; padding:10px 14px; font-weight:600; cursor:pointer; box-shadow:0 4px 12px rgba(37,99,235,0.35); transition:transform .2s, box-shadow .2s; }
.upgrade-btn:hover { transform:translateY(-2px); box-shadow:0 6px 16px rgba(37,99,235,0.45); }
.upgrade-btn:active { transform:translateY(0); }
.cta.muted { text-align:center; font-size:13px; color:#475569; }
</style>
