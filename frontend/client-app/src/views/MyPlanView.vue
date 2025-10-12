<template>
  <div class="plan-page">
    <h1 class="page-title">Мой план</h1>
    <div v-if="loading" class="loading">Загрузка...</div>
    <div v-else-if="error" class="error">Ошибка: {{ error }}</div>
    <div v-else class="plan-content">
      <div class="plan-summary" :class="{ trial: isTrial, pro: isPro }">
        <h2>{{ planLabel }}</h2>
        <template v-if="isTrial">
          <p>Осталось <strong>{{ daysLeft }}</strong> {{ dayWord }} Trial периода.</p>
          <p v-if="trialEndsAt">До: {{ formatDate(trialEndsAt) }}</p>
          <div class="upgrade-actions">
            <button class="upgrade-btn" @click="upgrade('STARTER')" :disabled="upgradeLoading && upgradeTarget==='STARTER'">{{ (upgradeLoading && upgradeTarget==='STARTER') ? '...' : 'Перейти на Starter' }}</button>
            <button class="upgrade-btn alt" @click="upgrade('PRO')" :disabled="upgradeLoading && upgradeTarget==='PRO'">{{ (upgradeLoading && upgradeTarget==='PRO') ? '...' : 'Сразу на Pro' }}</button>
          </div>
        </template>
        <template v-else-if="isStarter">
          <p>Текущий план Starter активен.</p>
          <button class="upgrade-btn" @click="upgrade('PRO')" :disabled="upgradeLoading">{{ upgradeLoading ? '...' : 'Апгрейд до Pro' }}</button>
        </template>
        <template v-else-if="isPro">
          <p>План Pro активен. Максимальные лимиты.</p>
          <div class="current-badge">Активен</div>
        </template>
      </div>

      <div class="limits" v-if="usage">
        <h3>Использование и лимиты</h3>
        <table class="limits-table">
          <thead><tr><th>Ресурс</th><th>Текущее</th><th>Лимит</th></tr></thead>
          <tbody>
            <tr v-for="row in limitRows" :key="row.key">
              <td>{{ row.label }}</td>
              <td>{{ row.current }}</td>
              <td>{{ row.limit }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { billingUsageState, loadBillingUsage } from '@/billing/usageStore.js';
import axios from 'axios';

export default {
  name: 'MyPlanView',
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
    planLabel(){
      if (this.planCode === 'PRO') return 'Pro';
      if (this.planCode === 'STARTER') return 'Starter';
      return 'Trial';
    },
    isStarter(){ return this.planCode === 'STARTER'; },
    isPro(){ return this.planCode === 'PRO'; },
    limitRows(){
      const u = this.usage; if(!u) return [];
      const arr = [];
      const mapping = [
        ['users','Пользователи'],
        ['clients','Клиенты'],
        ['cases','Дела'],
        ['files','Файлы'],
        ['storage_mb','Хранилище (MB)'],
        ['tasks_month','Задачи / месяц'],
        ['reminders_active','Активные напоминания'],
        ['emails_month','Email / месяц'],
      ];
      mapping.forEach(([key,label])=>{
        const current = u.current?.[key] ?? 0;
        const limit = u.limits?.[key] ?? '-';
        arr.push({ key, label, current, limit });
      });
      return arr;
    },
    dayWord(){
      const d = this.daysLeft; if(d===1) return 'день'; if(d>=2 && d<=4) return 'дня'; return 'дней';
    }
  },
  methods:{
    formatDate(dt){ try { return new Date(dt).toLocaleString(); } catch(e){ return dt; } },
    async upgrade(target){
      this.upgradeTarget = target;
      this.upgradeLoading = true;
      try {
        const token = localStorage.getItem('user-token');
        await axios.post('http://127.0.0.1:8000/api/billing/upgrade/', { target_plan: target }, { headers:{ Authorization:`Token ${token}` }});
        await loadBillingUsage(true);
        this.$toast && this.$toast.success(`План обновлён до ${target}`);
      } catch(e){
        this.$toast && this.$toast.error('Не удалось обновить план');
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
.plan-summary { background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:24px; margin-bottom:28px; box-shadow:0 4px 14px rgba(0,0,0,0.04); display:flex; flex-direction:column; gap:8px; }
.plan-summary.trial { border-color:#3b82f6; }
.plan-summary.pro { border-color:#9333ea; }
.plan-summary h2 { margin:0 0 10px; font-size:22px; font-weight:600; }
.upgrade-actions { display:flex; gap:12px; flex-wrap:wrap; margin-top:4px; }
.upgrade-btn { background:linear-gradient(90deg,#2563eb,#1d4ed8); color:#fff; border:none; padding:12px 20px; border-radius:10px; font-weight:600; cursor:pointer; box-shadow:0 4px 14px rgba(37,99,235,0.35); }
.upgrade-btn.alt { background:linear-gradient(90deg,#9333ea,#7e22ce); }
.upgrade-btn:hover { filter:brightness(1.05); }
.current-badge { display:inline-block; background:#16a34a; color:#fff; padding:6px 12px; border-radius:8px; font-size:13px; font-weight:600; }
.limits h3 { font-size:18px; margin:0 0 14px; font-weight:600; }
.limits-table { width:100%; border-collapse:collapse; background:#fff; border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; box-shadow:0 2px 10px rgba(0,0,0,0.03); }
.limits-table th, .limits-table td { padding:10px 14px; text-align:left; font-size:14px; }
.limits-table thead { background:#f1f5f9; }
.limits-table thead th { font-weight:700; }
.limits-table tbody tr:nth-child(even){ background:#f8fafc; }
.loading, .error { padding:20px; }
</style>
