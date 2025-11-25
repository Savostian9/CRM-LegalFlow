// Simple reactive store for billing usage & trial info
import { reactive } from 'vue';
import axios from '@/axios-setup';

export const billingUsageState = reactive({
  loading: false,
  loaded: false,
  error: null,
  data: null,
  daysLeft: null,
  isTrial: false,
  trialEndsAt: null,
  // convenience flags (populated after load)
  isStarter: false,
  isPro: false,
});

export async function loadBillingUsage(force=false) {
  if (billingUsageState.loading) return;
  if (billingUsageState.loaded && !force) return;
  billingUsageState.loading = true;
  billingUsageState.error = null;
  try {
    const token = localStorage.getItem('user-token');
    if (!token) throw new Error('NO_TOKEN');
    const res = await axios.get('/api/billing/usage/', { headers: { Authorization: `Token ${token}` }});
    billingUsageState.data = res.data;
    const plan = res.data?.plan;
    billingUsageState.isTrial = plan === 'TRIAL';
    billingUsageState.isStarter = plan === 'STARTER';
    billingUsageState.isPro = plan === 'PRO';
    const trial = res.data?.trial || null;
    if (trial && trial.trial_ends_at) {
      billingUsageState.trialEndsAt = trial.trial_ends_at;
      const end = new Date(trial.trial_ends_at);
      const now = new Date();
      const diffMs = end - now;
      billingUsageState.daysLeft = diffMs > 0 ? Math.ceil(diffMs / (1000*60*60*24)) : 0;
    } else {
      billingUsageState.daysLeft = null;
    }
    billingUsageState.loaded = true;
  } catch (e) {
    billingUsageState.error = e?.message || 'LOAD_FAILED';
  } finally {
    billingUsageState.loading = false;
  }
}
