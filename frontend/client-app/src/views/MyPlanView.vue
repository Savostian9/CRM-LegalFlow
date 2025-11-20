<template>
  <div class="plan-page">
    <h1 class="page-title">{{ $t('billing.title') }}</h1>
    <div v-if="loading" class="loading">{{ $t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ $t('billing.error') }}: {{ error }}</div>
    <div v-else class="plan-content">
      <section class="plan-summary" :class="{ trial: isTrial, pro: isPro }">
        <div class="plan-summary__header">
          <span class="plan-summary__label">{{ $t('billing.plan.active') }}</span>
          <h2>{{ planLabel }}</h2>
        </div>
        <p v-if="isTrial">{{ $t('billing.trial.remaining', { days: daysLeft, dayWord: dayWord }) }}</p>
        <p v-if="isTrial && trialEndsAt">{{ $t('billing.trial.until', { date: formatDate(trialEndsAt) }) }}</p>
        <p v-else-if="isStarter">{{ $t('billing.plan.currentStarter') }}</p>
        <p v-else-if="isPro">{{ $t('billing.plan.proActive') }}</p>
        <p class="plan-summary__hint">{{ $t('pricing.subtitle') }}</p>
      </section>

      <section class="plans-selector">
        <h3>{{ $t('pricing.title') }}</h3>
        <p>{{ $t('pricing.subtitle') }}</p>
        <PricingPlans
          :current-plan="planCode"
          :loading-plan="upgradeLoading ? upgradeTarget : null"
          :allowed-targets="availableUpgradeTargets"
          @select="handlePlanSelect"
        />
      </section>

      <section class="limits" v-if="limitRows.length">
        <div class="limits__header">
          <h3>{{ $t('billing.usageLimits') }}</h3>
          <span class="limits__plan">{{ planLabel }}</span>
        </div>
        <div class="limits-grid">
          <article class="limit-card" v-for="row in limitRows" :key="row.key">
            <header class="limit-card__head">
              <span class="limit-card__label">{{ row.label }}</span>
            </header>
            <div class="limit-card__numbers">
              <span class="limit-card__current">{{ $t('billing.current') }}: <strong>{{ row.currentDisplay }}</strong></span>
              <span class="limit-card__limit">{{ $t('billing.limit') }}: <strong>{{ row.limitDisplay }}</strong></span>
            </div>
            <div v-if="row.progress !== null" class="limit-card__progress">
              <div class="limit-card__progress-track">
                <div class="limit-card__progress-bar" :style="{ width: row.progress + '%' }"></div>
              </div>
              <span class="limit-card__progress-value">{{ row.progress }}%</span>
            </div>
          </article>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { billingUsageState, loadBillingUsage } from '@/billing/usageStore.js';
import { PLAN_CATALOG, formatStorage } from '@/billing/planCatalog';
import PricingPlans from '@/components/PricingPlans.vue';
import axios from '@/axios-setup';

export default {
  name: 'MyPlanView',
  components: { PricingPlans },
  data(){
    return { upgradeLoading:false, upgradeTarget:null };
  },
  computed:{
    loading(){ return billingUsageState.loading && !billingUsageState.loaded; },
    error(){ return billingUsageState.error; },
    usage(){ return billingUsageState.data; },
    isTrial(){ return billingUsageState.isTrial; },
    daysLeft(){ return billingUsageState.daysLeft; },
    trialEndsAt(){ return billingUsageState.trialEndsAt; },
    planCode(){ return (this.usage?.plan || 'TRIAL').toUpperCase(); },
    planMeta(){
      return PLAN_CATALOG[this.planCode] || null;
    },
    planLabel(){
      if (this.planCode === 'PRO') return 'Pro';
      if (this.planCode === 'STARTER') return 'Starter';
      return 'Trial';
    },
    isStarter(){ return this.planCode === 'STARTER'; },
    isPro(){ return this.planCode === 'PRO'; },
    availableUpgradeTargets(){
      const map = {
        TRIAL: ['STARTER', 'PRO'],
        STARTER: ['PRO'],
        PRO: ['STARTER']
      };
      return map[this.planCode] || [];
    },
    limitRows(){
      const u = this.usage;
      if (!u) return [];
      const planLimits = this.planMeta?.limits || {};
      const t = (k)=> this.$t(`billing.rows.${k}`);
      const map = [
        { key: 'users', planKey: 'users', label: t('users') },
        { key: 'clients', planKey: 'clients', label: t('clients') },
        { key: 'storage_mb', planKey: 'files_storage_mb', label: t('storageMb'), formatter: 'storage' },
        { key: 'tasks_month', planKey: 'tasks_per_month', label: t('tasksMonth') },
        { key: 'emails_month', planKey: 'emails_per_month', label: t('emailsMonth') },
      ];
      return map.map((item)=>{
        const currentRaw = u.current?.[item.key] ?? 0;
        const limitRaw = (planLimits[item.planKey] ?? u.limits?.[item.key] ?? null);
        const { currentDisplay, limitDisplay, progress } = this.formatLimitRow(item.formatter, currentRaw, limitRaw);
        return {
          key: item.key,
          label: item.label,
          currentDisplay,
          limitDisplay,
          progress,
        };
      });
    },
    dayWord(){
      const d = this.daysLeft || 0;
      const loc = (this.$i18n && this.$i18n.locale) || 'ru';
      if (loc.startsWith('pl')) return d === 1 ? 'dzień' : 'dni';
      if (d===1) return 'день'; if(d>=2 && d<=4) return 'дня'; return 'дней';
    }
  },
  methods:{
    formatLimitRow(type, currentRaw, limitRaw){
      const locale = (this.$i18n && this.$i18n.locale) || 'ru';
      const numberFormatter = new Intl.NumberFormat(locale === 'pl' ? 'pl-PL' : 'ru-RU', { maximumFractionDigits: 0 });
      const toNumber = (value)=>{
        if (value === null || value === undefined) return null;
        const num = Number(value);
        return Number.isFinite(num) ? num : null;
      };
      const currentNum = toNumber(currentRaw) ?? 0;
      const limitNum = toNumber(limitRaw);
      const unlimited = typeof limitNum === 'number' && limitNum >= 1000000;

      const formatGeneric = (val)=> numberFormatter.format(Math.max(0, Math.floor(val || 0)));
      let currentDisplay;
      let limitDisplay;

      if (type === 'storage') {
        currentDisplay = formatStorage(currentNum || 0);
        limitDisplay = unlimited ? this.$t('billing.limitUnlimited') : limitNum !== null ? formatStorage(limitNum) : '—';
      } else {
        currentDisplay = formatGeneric(currentNum);
        if (unlimited) {
          limitDisplay = this.$t('billing.limitUnlimited');
        } else if (limitNum !== null) {
          limitDisplay = formatGeneric(limitNum);
        } else {
          limitDisplay = '—';
        }
      }

      let progress = null;
      if (!unlimited && limitNum && limitNum > 0) {
        progress = Math.min(100, Math.round((currentNum / limitNum) * 100));
      }

      return { currentDisplay, limitDisplay, progress };
    },
    handlePlanSelect(planCode){
      const target = (planCode || '').toUpperCase();
      if (!target) { return; }
      if (target === this.planCode) {
        if (this.$toast) {
          const message = this.$t('billing.plan.active');
          if (typeof this.$toast.info === 'function') {
            this.$toast.info(message);
          } else if (typeof this.$toast.success === 'function') {
            this.$toast.success(message);
          }
        }
        return;
      }
      this.upgrade(target);
    },
    formatDate(dt){ try { return new Date(dt).toLocaleString(); } catch(e){ return dt; } },
    async upgrade(target){
      this.upgradeTarget = target;
      this.upgradeLoading = true;
      try {
        const token = localStorage.getItem('user-token');
        await axios.post('/api/billing/upgrade/', { target_plan: target }, { headers:{ Authorization:`Token ${token}` }});
        await loadBillingUsage(true);
        this.$toast && this.$toast.success(this.$t('billing.toast.upgraded', { plan: target }));
      } catch(e){
        this.$toast && this.$toast.error(this.$t('billing.toast.upgradeFailed'));
      } finally {
        this.upgradeLoading = false;
        this.upgradeTarget = null;
      }
    }
  },
  async created(){
    await loadBillingUsage();
  }
}
</script>

<style scoped>
.plan-page { padding:24px 28px; }
.page-title { font-size:24px; font-weight:600; margin:0 0 22px; }
.plan-summary { background:#fff; border:1px solid #e2e8f0; border-radius:16px; padding:26px 32px; margin-bottom:32px; box-shadow:0 10px 30px rgba(15,23,42,0.06); display:flex; flex-direction:column; gap:10px; }
.plan-summary.trial { border-color:#3b82f6; box-shadow:0 12px 32px rgba(37,99,235,0.12); }
.plan-summary.pro { border-color:#9333ea; box-shadow:0 12px 32px rgba(147,51,234,0.12); }
.plan-summary__header { display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap; }
.plan-summary__label { font-size:12px; letter-spacing:0.08em; text-transform:uppercase; background:rgba(37,99,235,0.12); color:#1d4ed8; padding:6px 12px; border-radius:999px; font-weight:700; }
.plan-summary h2 { margin:0; font-size:28px; font-weight:700; color:#0f172a; }
.plan-summary p { margin:0; color:#475569; font-size:15px; }
.plan-summary__hint { margin-top:12px; font-size:14px; color:#64748b; }

.plans-selector { margin-bottom:36px; text-align:center; }
.plans-selector h3 { margin:0 0 8px; font-size:22px; font-weight:700; color:#0f172a; }
.plans-selector p { margin:0 0 28px; color:#64748b; font-size:15px; }
.limits { background:#fff; border:1px solid #e2e8f0; border-radius:16px; padding:28px 32px; box-shadow:0 10px 30px rgba(15,23,42,0.05); }
.limits__header { display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:24px; flex-wrap:wrap; }
.limits__header h3 { margin:0; font-size:20px; font-weight:700; color:#0f172a; }
.limits__plan { display:inline-flex; align-items:center; gap:6px; background:rgba(14,165,233,0.12); color:#0369a1; padding:6px 12px; border-radius:999px; font-weight:600; font-size:13px; }
.limits-grid { display:grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap:18px; }
.limit-card { background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:18px 20px; display:flex; flex-direction:column; gap:12px; box-shadow:0 6px 18px rgba(15,23,42,0.04); }
.limit-card__label { font-size:15px; font-weight:600; color:#1e293b; }
.limit-card__numbers { display:flex; flex-direction:column; gap:6px; font-size:14px; color:#475569; }
.limit-card__numbers strong { color:#0f172a; font-weight:700; }
.limit-card__progress { display:flex; align-items:center; gap:10px; }
.limit-card__progress-track { flex:1; height:8px; border-radius:999px; background:#e2e8f0; overflow:hidden; }
.limit-card__progress-bar { height:100%; background:linear-gradient(90deg,#2563eb,#7c3aed); border-radius:999px; transition:width 0.3s ease; }
.limit-card__progress-value { font-size:12px; font-weight:600; color:#475569; min-width:34px; text-align:right; }
.loading, .error { padding:20px; }
</style>
