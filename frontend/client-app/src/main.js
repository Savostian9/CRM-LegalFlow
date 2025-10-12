import { createApp } from 'vue'
// Initialize global axios config (baseURL + URL rewrite)
import './axios-setup'
import App from './App.vue'
import router from './router' // Убедитесь, что роутер импортируется,
import VueTelInput from 'vue-tel-input' // <-- ДОБАВЬТЕ ЭТУ СТРОКУ
import 'vue-tel-input/vue-tel-input.css'
import './styles/forms.css'
import i18n from './i18n'

const app = createApp(App)

app.use(router) // <--- ВОТ ЭТА СТРОКА ВСЁ ИСПРАВИТ
app.use(VueTelInput)
app.use(i18n)

// Инициализация темы из localStorage
const savedTheme = localStorage.getItem('theme') || 'light'
const savedLocale = localStorage.getItem('locale') || i18n.global.locale || 'ru'
document.documentElement.setAttribute('data-theme', savedTheme)
document.documentElement.setAttribute('lang', savedLocale)

app.mount('#app')