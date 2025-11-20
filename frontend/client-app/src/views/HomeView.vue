<template>
  <div class="home-container">
    <header class="header">
      <div class="logo">
        <router-link to="/">LegalFlow</router-link>
      </div>
      <nav class="auth-buttons">
  <LangSwitcher />
  <button class="button secondary" @click="scrollToPricing" type="button">{{ $t('home.pricing') }}</button>
        <router-link to="/login" class="button secondary">{{ $t('home.login') }}</router-link>
        <router-link to="/register" class="button primary">{{ $t('home.getStarted') }}</router-link>
      </nav>
    </header>

    <main class="hero-section">
      <div class="hero-content">
        <h1 class="hero-headline">
          {{ $t('home.headline') }}
        </h1>
        <p class="hero-subheadline">
          {{ $t('home.subheadline') }}
        </p>
        <router-link to="/register" class="button primary cta-button">{{ $t('home.cta') }}</router-link>
      </div>
      <div class="hero-graphic" aria-hidden="true">
        <div class="docs-illustration">
          <!-- Main document card -->
          <div class="doc-card doc-main">
            <div class="doc-bar"></div>
            <div class="doc-line w-80"></div>
            <div class="doc-line w-60"></div>
            <div class="doc-sep"></div>
            <div class="doc-row">
              <span class="doc-check checked">✓</span>
              <span class="doc-text w-75"></span>
            </div>
            <div class="doc-row">
              <span class="doc-check checked">✓</span>
              <span class="doc-text w-55"></span>
            </div>
            <div class="doc-row">
              <span class="doc-check"></span>
              <span class="doc-text w-65 light"></span>
            </div>
          </div>
          <!-- Secondary document card -->
          <div class="doc-card doc-side">
            <div class="doc-bar small"></div>
            <div class="doc-line w-70"></div>
            <div class="doc-line w-50"></div>
            <div class="doc-sep"></div>
            <div class="doc-row">
              <span class="doc-check checked">✓</span>
              <span class="doc-text w-60"></span>
            </div>
            <div class="doc-row">
              <span class="doc-check"></span>
              <span class="doc-text w-50 light"></span>
            </div>
          </div>
        </div>
      </div>
    </main>
    <section id="pricing" class="pricing-section">
      <h2 class="pricing-heading">{{ $t('pricing.title') }}</h2>
      <p class="pricing-sub">{{ $t('pricing.subtitle') }}</p>
      <PricingPlans :show-trial="true" @select="onSelectPlan" />
    </section>
    <footer class="footer">
      <router-link to="/privacy-policy">Polityka prywatności</router-link>
      <router-link to="/cookies-policy">Polityka cookies</router-link>
      <router-link to="/terms">Regulamin Serwisu</router-link>
    </footer>
  </div>
</template>

<script>
import LangSwitcher from '@/components/LangSwitcher.vue'
import PricingPlans from '@/components/PricingPlans.vue'
export default {
  name: 'HomeView',
  components: { LangSwitcher, PricingPlans },
  methods: {
    onSelectPlan(plan){
      if (plan === 'STARTER') {
        this.$router.push('/register');
      }
    },
    scrollToPricing(){
      const el = document.getElementById('pricing');
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  }
}
</script>

<style scoped>
/* Импорт современного шрифта */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

/* Анимация появления */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

:root {
  --primary-color: #4A90E2;
  --primary-hover: #357ABD;
  --dark-blue: #2c3e50;
  --text-color: #5a6a7b;
  --background-color: #f7f9fc;
  --white-color: #ffffff;
  --border-color: #e0e6ed;
}

.home-container {
  font-family: 'Inter', sans-serif;
  background-color: var(--white-color);
  color: var(--text-color);
  min-height: 100vh;
  overflow-x: hidden; /* Предотвращаем горизонтальный скролл */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 60px;
  border-bottom: 1px solid var(--border-color);
}

.logo a {
  font-size: 26px;
  font-weight: 700;
  text-decoration: none;
  color: var(--dark-blue);
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 18px;
}

.button {
  padding: 12px 24px;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.3s ease;
  border: 1px solid transparent;
  white-space: nowrap; /* Запрещаем перенос текста на кнопках */
}


.button.primary {
  background: linear-gradient(90deg, #2563eb 0%, #4A90E2 100%);
  color: #fff !important;
  border-radius: 14px;
  font-weight: 700;
  box-shadow: 0 6px 24px rgba(74,144,226,0.18);
  letter-spacing: 0.02em;
  border: none;
  transition: background 0.25s, box-shadow 0.18s, transform 0.18s;
  position: relative;
  overflow: hidden;
}
.button.primary::after {
  content: "";
  position: absolute;
  left: -60%;
  top: 0;
  width: 60%;
  height: 100%;
  background: linear-gradient(120deg, rgba(255,255,255,0) 0%, rgba(255,255,255,.25) 50%, rgba(255,255,255,0) 100%);
  transform: skewX(-18deg);
  opacity: 0;
  pointer-events: none;
}
.button.primary:hover {
  background: linear-gradient(90deg, #357ABD 0%, #2563eb 100%);
  box-shadow: 0 10px 32px rgba(74,144,226,0.22);
  transform: translateY(-2px) scale(1.04);
}
.button.primary:hover::after {
  animation: btnShine 0.9s ease;
  opacity: 1;
}
@keyframes btnShine {
  0% { transform:translateX(0) skewX(-18deg); opacity:0; }
  30% { opacity:.7; }
  60% { opacity:.3; }
  100% { transform:translateX(260%) skewX(-18deg); opacity:0; }
}

.button.secondary {
  background-color: #f0f2f5;
  color: var(--dark-blue);
  border-color: transparent;
  font-size: 1em;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.button.secondary:hover {
  background-color: #e4e6e9;
  color: var(--dark-blue);
}

.hero-section {
  display: grid;
  grid-template-columns: 1fr 0.8fr;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 60px;
  gap: 40px;
}

.pricing-section { max-width:1200px; margin:50px auto 40px; padding:0 60px 10px; }
.pricing-heading { font-size:2.4em; font-weight:700; color:var(--dark-blue); margin:0 0 10px; text-align:center; }
.pricing-sub { text-align:center; margin:0 0 28px; font-size:1.05em; color:#4b5563; }
/* removed bottom CTA button */

.hero-content {
  animation: fadeInUp 0.8s ease-out;
}

.hero-headline {
  font-size: 3.2em;
  font-weight: 700;
  color: var(--dark-blue);
  line-height: 1.2;
  margin-bottom: 25px;
}

.hero-subheadline {
  font-size: 1.15em;
  line-height: 1.7;
  max-width: 500px;
  margin-bottom: 40px;
}

.cta-button {
  font-size: 1.1em;
  padding: 18px 36px;
}

.hero-graphic {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeInUp 0.8s ease-out 0.2s;
  animation-fill-mode: backwards;
}

/* Documents illustration */
.docs-illustration { position: relative; width: 440px; height: 460px; }
.doc-card {
  position: absolute;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 18px 40px rgba(0,0,0,.16);
  border: 1px solid rgba(0,0,0,.06);
  padding: 18px 18px 22px;
}
.doc-main { width: 320px; height: 420px; transform: rotate(-10deg); left: 40px; top: 10px; }
.doc-side { width: 200px; height: 280px; transform: rotate(8deg); right: 10px; bottom: 20px; }

.doc-bar { height: 16px; border-radius: 10px; margin-bottom: 14px; background: linear-gradient(90deg, var(--primary-color), #81c784); }
.doc-bar.small { height: 12px; }

.doc-line { height: 10px; background: #e9eef6; border-radius: 8px; margin: 8px 0; }
.doc-line.w-80 { width: 80%; }
.doc-line.w-70 { width: 70%; }
.doc-line.w-65 { width: 65%; }
.doc-line.w-60 { width: 60%; }
.doc-line.w-55 { width: 55%; }
.doc-line.w-50 { width: 50%; }

.doc-sep { height: 1px; background: #e5e7eb; margin: 14px 0; }

.doc-row { display: flex; align-items: center; gap: 10px; margin: 10px 0; }
.doc-check {
  width: 18px; height: 18px; border-radius: 50%; border: 2px solid #d1d5db; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; line-height: 1; color: #10b981; background: #fff;
}
.doc-check.checked { border-color: #10b981; background: #ecfdf5; }
.doc-text { height: 10px; background: #e9eef6; border-radius: 6px; display: inline-block; flex-shrink: 0; }
.doc-text.light { background: #f1f5f9; }
.doc-text.w-75 { width: 75%; }
.doc-text.w-60 { width: 60%; }
.doc-text.w-55 { width: 55%; }
.doc-text.w-50 { width: 50%; }

/* subtle floating */
.doc-main { animation: floatA 6s ease-in-out infinite; }
.doc-side { animation: floatB 6s ease-in-out infinite; animation-delay: .6s; }
@keyframes floatA { 0%,100% { transform: translateY(0) rotate(-10deg); } 50% { transform: translateY(-6px) rotate(-10deg); } }
@keyframes floatB { 0%,100% { transform: translateY(0) rotate(8deg); } 50% { transform: translateY(6px) rotate(8deg); } }

/* --- НАЧАЛО АДАПТИВНОСТИ --- */

/* Планшеты (до 992px) */
@media (max-width: 992px) {
  .header {
    padding: 20px 40px;
  }

  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 60px 40px;
  }

  .hero-graphic {
    display: none; /* Скрываем графику на планшетах и телефонах */
  }

  .hero-subheadline {
    margin-left: auto;
    margin-right: auto;
  }

  .hero-headline {
    font-size: 2.8em; /* Немного уменьшаем заголовок */
  }
}

/* Телефоны (до 576px) */
@media (max-width: 576px) {
  .header {
    padding: 15px 20px;
  }

  .logo a {
    font-size: 22px; /* Уменьшаем логотип */
  }
  
  .button {
    padding: 10px 16px; /* Уменьшаем кнопки */
    font-size: 0.9em;
  }

  .hero-section {
    padding: 40px 20px;
  }

  .hero-headline {
    font-size: 2.2em; /* Значительно уменьшаем заголовок */
  }

  .hero-subheadline {
    font-size: 1em;
  }

  .cta-button {
    font-size: 1em;
    padding: 15px 30px;
  }
}
/* --- КОНЕЦ АДАПТИВНОСТИ --- */

/* Footer with policy links */
.footer {
  border-top: 1px solid var(--border-color);
  padding: 20px 60px;
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}
.footer a { color: var(--dark-blue); text-decoration: none; opacity: 0.8; }
.footer a:hover { opacity: 1; text-decoration: underline; }
</style>