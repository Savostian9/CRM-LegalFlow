<template>
  <div class="pricing-wrapper">
    <h3 class="pricing-title">{{ $t('pricing.title') }}</h3>
    <div class="pricing-grid">
      <div
        v-for="plan in plans"
        :key="plan.code"
        class="plan-card"
        :class="plan.code.toLowerCase()"
      >
        <div class="plan-head">
          <h4>{{ plan.name }}</h4>
          <span v-if="planBadge(plan)" class="badge" :class="{ primary: plan.highlight }">{{ planBadge(plan) }}</span>
        </div>
        <div class="price">
          <template v-if="plan.price === 0">0 PLN <span>/ {{ pricePeriodLabel(plan) }}</span></template>
          <template v-else>{{ plan.price }} PLN <span>/ {{ pricePeriodLabel(plan) }}</span></template>
        </div>
        <p class="desc">{{ $t(`pricing.plans.${plan.code}.description`) }}</p>
        <ul class="features">
          <li v-for="(f, idx) in plan.features" :key="idx">{{ $t(`pricing.plans.${plan.code}.features.${idx}`) }}</li>
        </ul>
        <!-- Детали всегда показаны -->
        <div class="details">
          <h5>{{ $t('pricing.includesTitle') }}</h5>
          <table class="limits-table">
            <tbody>
              <tr>
                <td>{{ $t('pricing.fields.users') }}</td>
                <td>{{ plan.limits.users }}</td>
              </tr>
              <tr>
                <td>{{ $t('pricing.fields.clients') }}</td>
                <td>{{ plan.limits.clients }}</td>
              </tr>
              <tr>
                <td>{{ $t('pricing.fields.cases') }}</td>
                <td>{{ plan.limits.cases }}</td>
              </tr>
              <tr>
                <td>{{ $t('pricing.fields.files') }}</td>
                <td>{{ plan.limits.files }}</td>
              </tr>
              <tr>
                <td>{{ $t('pricing.fields.storage') }}</td>
                <td>{{ formatStorage(plan.limits.files_storage_mb) }}</td>
              </tr>
              <tr>
                <td>{{ $t('pricing.fields.tasksPerMonth') }}</td>
                <td>{{ plan.limits.tasks_per_month }}</td>
              </tr>
              <tr>
                <td>{{ $t('pricing.fields.remindersActive') }}</td>
                <td>{{ plan.limits.reminders_active }}</td>
              </tr>
              <tr>
                <td>{{ $t('pricing.fields.emailsPerMonth') }}</td>
                <td>{{ plan.limits.emails_per_month }}</td>
              </tr>
            </tbody>
          </table>
          <div class="qualitative" v-if="plan.qualitative?.length">
            <h5>{{ $t('pricing.additionalTitle') }}</h5>
            <ul class="qual-list">
              <li v-for="q in plan.qualitative" :key="q.key">{{ $t(`pricing.qual.labels.${q.key}`) }}: <strong>{{ $t(`pricing.qual.values.${q.key}.${plan.code}`) }}</strong></li>
            </ul>
          </div>
        </div>
        <div class="actions">
          <button
            v-if="plan.code !== 'TRIAL'"
            class="upgrade-btn"
            @click="$emit('select', plan.code)"
          >
            {{ $t('pricing.actions.select') }}
          </button>
          <div v-else class="cta muted">{{ $t('pricing.actions.trialCta') }}</div>
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
    formatStorage(mb) { return formatStorage(mb); },
    pricePeriodLabel(plan){
      const raw = (plan.pricePeriod || '').toLowerCase();
      if (raw.includes('месяц') || raw.includes('month')) return this.$t('pricing.pricePeriod.month');
      return this.$t('pricing.pricePeriod.period');
    },
    planBadge(plan){
      const k = `pricing.plans.${plan.code}.badge`;
      try { return this.$t(k); } catch(e){ return plan.badge; }
    }
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
.badge.primary { background: var(--primary-color, #4A90E2); color:#fff; }
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
.upgrade-btn {
  background: var(--primary-color, #4A90E2);
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 10px 14px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(74, 144, 226, 0.2);
  transition: all 0.2s ease;
}
.upgrade-btn:hover {
  background: #ffffff;
  color: #000000 !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}
.upgrade-btn:active { transform: translateY(0); }
.cta.muted { text-align:center; font-size:13px; color:#475569; }
</style>
