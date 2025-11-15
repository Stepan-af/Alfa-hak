import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'
import './design/tokens.css'
import './assets/animations.css'
import App from './App.vue'
import router from './router'

const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'alfaDark',
    themes: {
      alfaDark: {
        dark: true,
        colors: {
          primary: '#ef3124',
          secondary: '#1a1b1e',
          background: '#0f0f10',
          surface: '#1a1b1e',
          error: '#ef4444',
          info: '#3b82f6',
          success: '#22c55e',
          warning: '#f59e0b',
        }
      }
    }
  }
})

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(vuetify)

// Wait for router to be ready before mounting
router.isReady().then(() => {
  app.mount('#app')
})
