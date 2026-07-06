import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'
import App from './App.vue'
import router from './router'
import { useThemeStore } from './stores/theme'
import { AppPreset, DARK_MODE_SELECTOR } from './theme/preset'
import 'primeicons/primeicons.css'
import './assets/styles/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
useThemeStore()
app.use(PrimeVue, {
  theme: {
    preset: AppPreset,
    options: {
      darkModeSelector: DARK_MODE_SELECTOR,
      cssLayer: {
        name: 'primevue',
        order: 'tailwind-base, primevue, tailwind-utilities',
      },
    },
  },
})
app.use(ToastService)
app.use(ConfirmationService)
app.mount('#app')
