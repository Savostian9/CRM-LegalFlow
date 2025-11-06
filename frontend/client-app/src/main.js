import { createApp } from 'vue'
// Initialize global axios config (baseURL + URL rewrite)
import './axios-setup'
import App from './App.vue'
import router from './router' // Убедитесь, что роутер импортируется,
import VueTelInput from 'vue-tel-input' // <-- ДОБАВЬТЕ ЭТУ СТРОКУ
import 'vue-tel-input/vue-tel-input.css'
import './styles/forms.css'
import i18n from './i18n'
import UiSelect from './components/UiSelect.vue'
import ClientAutocomplete from './components/ClientAutocomplete.vue'
import UiDateTimePicker from './components/UiDateTimePicker.vue'
import AltDateTimePicker from './components/AltDateTimePicker.vue'
import VCalendar from 'v-calendar'
import 'v-calendar/style.css'

const app = createApp(App)

app.use(router) // <--- ВОТ ЭТА СТРОКА ВСЁ ИСПРАВИТ
app.use(VueTelInput)
app.use(i18n)
app.use(VCalendar, {})
// Global components so they can be used in any view's template without local imports
app.component('UiSelect', UiSelect)
app.component('ClientAutocomplete', ClientAutocomplete)
app.component('UiDateTimePicker', UiDateTimePicker)
app.component('AltDateTimePicker', AltDateTimePicker)

// Инициализация темы из localStorage
const savedTheme = localStorage.getItem('theme') || 'light'
const savedLocale = localStorage.getItem('locale') || i18n.global.locale || 'ru'
document.documentElement.setAttribute('data-theme', savedTheme)
document.documentElement.setAttribute('lang', savedLocale)

app.mount('#app')