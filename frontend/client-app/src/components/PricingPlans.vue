<template>
  <div class="pricing-wrapper">

    <div class="billing-cycle-toggle" role="tablist" aria-label="Billing cycle">
      <span
        class="segmented-thumb"
        :style="{ transform: billingCycle === 'month' ? 'translateX(0)' : 'translateX(100%)' }"
        aria-hidden="true"
      />
      <button 
        class="cycle-btn" 
        :class="{ active: billingCycle === 'month' }"
        role="tab"
        :aria-selected="billingCycle === 'month'"
        @click="setCycle('month')"
      >
        {{ $t('pricing.pricePeriod.month') }}
      </button>
      <button 
        class="cycle-btn" 
        :class="{ active: billingCycle === 'year' }"
        role="tab"
        :aria-selected="billingCycle === 'year'"
        @click="setCycle('year')"
      >
        {{ $t('pricing.pricePeriod.year') }} <span class="discount">-20%</span>
      </button>
    </div>

    <div class="pricing-grid">
      <div
        v-for="plan in plans"
        :key="plan.code"
        class="plan-card"
        :class="[plan.code.toLowerCase(), { 'is-current': isCurrentPlan(plan.code) }]"
      >
        <div class="plan-head">
          <h4>{{ plan.name }}</h4>
          <span v-if="planBadge(plan)" class="badge" :class="{ primary: plan.highlight }">{{ planBadge(plan) }}</span>
          <span v-if="isCurrentPlan(plan.code)" class="current-chip">{{ currentText }}</span>
        </div>
        <div class="price">
          <template v-if="currentPrice(plan) === 0">0 zł <span>/ {{ pricePeriodLabel(plan) }}</span></template>
          <template v-else>{{ currentPrice(plan) }} zł <span>/ {{ pricePeriodLabel(plan) }}</span></template>
          <div v-if="billingCycle === 'year' && plan.price > 0" class="billed-yearly-hint">
            * {{ $t('pricing.billedYearly') }}
          </div>
        </div>
        <p class="desc">{{ $t(`pricing.plans.${plan.code}.description`) }}</p>
        <ul class="features">
          <li v-for="(f, idx) in plan.features" :key="idx">{{ $t(`pricing.plans.${plan.code}.features.${idx}`) }}</li>
        </ul>
        
        <div class="actions">
          <button
            v-if="plan.code !== 'TRIAL'"
            class="upgrade-btn"
            :class="{
              loading: loadingPlan === plan.code,
              active: isCurrentPlan(plan.code),
              unavailable: !isPlanSelectable(plan.code) && !isCurrentPlan(plan.code)
            }"
            :disabled="loadingPlan === plan.code || isCurrentPlan(plan.code) || !isPlanSelectable(plan.code)"
            @click="onSelect(plan.code)"
          >
            <span v-if="isCurrentPlan(plan.code)">{{ currentText }}</span>
            <span v-else-if="loadingPlan === plan.code">{{ loadingText }}</span>
            <span v-else-if="!isPlanSelectable(plan.code)">{{ unavailableText }}</span>
            <span v-else>{{ selectText }}</span>
          </button>
          <div v-else class="cta muted">{{ $t('pricing.actions.trialCta') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getPlanCatalogArray } from '../billing/planCatalog';
export default {
  name: 'PricingPlans',
  props: {
    showTrial: { type: Boolean, default: true },
    currentPlan: { type: String, default: null },
    loadingPlan: { type: String, default: null },
    allowedTargets: { type: Array, default: () => null },
    selectLabel: { type: String, default: '' },
    currentLabel: { type: String, default: '' },
    processingLabel: { type: String, default: '' },
    unavailableLabel: { type: String, default: '' },
    billingCycle: { type: String, default: 'month' }
  },
  emits: ['select', 'update:billingCycle'],
  computed: {
    plans() {
      const all = getPlanCatalogArray();
      return this.showTrial ? all : all.filter(p => p.code !== 'TRIAL');
    },
    normalizedCurrentPlan() {
      return this.currentPlan ? this.currentPlan.toUpperCase() : null;
    },
    selectText() {
      return this.selectLabel || this.$t('pricing.actions.select');
    },
    currentText() {
      return this.currentLabel || this.$t('billing.plan.active');
    },
    loadingText() {
      return this.processingLabel || this.$t('common.processing');
    },
    unavailableText() {
      return this.unavailableLabel || this.$t('billing.plan.unavailable');
    },
    allowedSet() {
      if (!Array.isArray(this.allowedTargets)) return null;
      return new Set(this.allowedTargets.map(code => String(code).toUpperCase()));
    }
  },
  methods: {
    setCycle(val) {
      this.$emit('update:billingCycle', val);
    },
    currentPrice(plan) {
      if (this.billingCycle === 'year' && plan.priceYearly !== undefined) {
        return plan.priceYearly;
      }
      return plan.price;
    },
    pricePeriodLabel(plan){
      // If trial or special period
      if (plan.pricePeriod === 'период' || plan.pricePeriod === 'period') {
        return this.$t('pricing.pricePeriod.period');
      }
      // Otherwise it's per month (even if billed yearly, the price shown is per month)
      return this.$t('pricing.pricePeriod.month');
    },
    planBadge(plan){
      const k = `pricing.plans.${plan.code}.badge`;
      try { return this.$t(k); } catch(e){ return plan.badge; }
    },
    isCurrentPlan(code) {
      if (!code) return false;
      return this.normalizedCurrentPlan === code.toUpperCase();
    },
    isPlanSelectable(code) {
      if (!code) return false;
      const upper = code.toUpperCase();
      if (this.isCurrentPlan(upper)) return true;
      if (!this.allowedSet) return true;
      return this.allowedSet.has(upper);
    },
    onSelect(code) {
      if (!code) return;
      if (!this.isPlanSelectable(code) || this.isCurrentPlan(code) || this.loadingPlan === code) {
        return;
      }
      this.$emit('select', code);
    }
  }
}
</script>

<style scoped>
.pricing-wrapper { margin-top: 0; }

.billing-cycle-toggle {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 1fr;
  align-items: center;
  gap: 0;
  background: #eef2f7;
  padding: 6px;
  border-radius: 999px;
  width: fit-content;
  margin: 6px auto 28px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06);
}
.billing-cycle-toggle .segmented-thumb {
  position: absolute;
  top: 6px;
  left: 6px;
  width: calc(50% - 6px);
  height: calc(100% - 12px);
  background: #ffffff;
  border-radius: 999px;
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.14);
  transition: transform 0.25s ease;
}
.cycle-btn {
  position: relative;
  z-index: 1;
  border: none;
  background: transparent;
  padding: 10px 24px;
  border-radius: 999px;
  font-weight: 700;
  color: #475569;
  cursor: pointer;
  transition: color 0.2s ease, transform 0.12s ease;
  font-size: 14px;
}
.cycle-btn:hover { color: #0f172a; }
.cycle-btn:active { transform: translateY(1px); }
.cycle-btn.active { color: #0f172a; }
.cycle-btn .discount {
  font-size: 11px;
  color: #2563eb;
  background: #eff6ff;
  padding: 2px 6px;
  border-radius: 99px;
  margin-left: 6px;
}

.pricing-grid { display:grid; gap:24px; grid-template-columns: repeat(auto-fit,minmax(280px,1fr)); max-width: 1100px; margin: 0 auto; }
.plan-card { background:#fff; border:1px solid #e2e8f0; border-radius:16px; padding:24px; position:relative; display:flex; flex-direction:column; box-shadow:0 4px 12px rgba(0,0,0,0.04); transition: transform 0.2s ease, box-shadow 0.2s ease; }
.plan-card:hover { transform: translateY(-4px); box-shadow: 0 12px 24px rgba(0,0,0,0.08); }
.plan-card.is-current { border-color:#2563eb; box-shadow:0 18px 34px rgba(37,99,235,0.18); transform: translateY(-6px); }
.plan-card.is-current .badge { background: rgba(37,99,235,0.14); color:#1d4ed8; }

.plan-card.trial { border-color:#cbd5e1; }
.plan-card.starter { border-color:#3b82f6; border-width: 2px; }
.plan-card.pro { border-color:#9333ea; }

.plan-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; gap:10px; }
.plan-head h4 { font-size:20px; margin:0; font-weight:700; color: #1e293b; flex:1; }
.badge { background:#f1f5f9; color:#475569; font-size:12px; padding:4px 10px; border-radius:20px; font-weight:600; }
.badge.primary { background: #eff6ff; color:#2563eb; }
.current-chip { display:inline-flex; align-items:center; gap:6px; background: rgba(37,99,235,0.12); color:#1d4ed8; border-radius:999px; padding:4px 10px; font-weight:600; font-size:12px; }

.price { font-size:32px; font-weight:800; margin:12px 0 4px; color: #0f172a; line-height: 1.2; }
.price span { font-size:15px; font-weight:500; color:#64748b; }
.billed-yearly-hint { font-size: 12px; color: #64748b; font-weight: 400; margin-top: 4px; }

.desc { font-size:14px; color:#64748b; margin:0 0 20px; line-height:1.5; min-height: 42px; }

.features { list-style:none; padding:0; margin:0 0 24px; font-size:14px; color:#334155; display:flex; flex-direction:column; gap:10px; flex: 1; }
.features li { position:relative; padding-left:24px; line-height: 1.4; }
.features li:before { content:'✔'; position:absolute; left:0; top:2px; color:#2563eb; font-weight: bold; font-size:14px; }

.actions { margin-top:auto; display:flex; flex-direction:column; gap:8px; }
.upgrade-btn {
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 12px 16px;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  font-size: 15px;
  transition: all 0.2s ease;
}
.upgrade-btn:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
.upgrade-btn:active { transform: translateY(0); }
.upgrade-btn.active {
  background: #1d4ed8;
  box-shadow: none;
  cursor: default;
  transform: none;
}
.upgrade-btn.loading {
  background: #94a3b8;
  color: #e2e8f0;
  box-shadow: none;
  cursor: wait;
  transform: none;
}
.upgrade-btn.unavailable {
  background: #e2e8f0;
  color: #94a3b8;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}
.upgrade-btn.unavailable:hover {
  background: #e2e8f0;
  color: #94a3b8;
}
.cta.muted { text-align:center; font-size:14px; color:#64748b; padding: 12px; background: #f8fafc; border-radius: 10px; font-weight: 500; }
</style>
