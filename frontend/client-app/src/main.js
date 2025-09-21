import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Убедитесь, что роутер импортируется,
import VueTelInput from 'vue-tel-input' // <-- ДОБАВЬТЕ ЭТУ СТРОКУ
import 'vue-tel-input/vue-tel-input.css'

const app = createApp(App)

app.use(router) // <--- ВОТ ЭТА СТРОКА ВСЁ ИСПРАВИТ
app.use(VueTelInput)

app.mount('#app')