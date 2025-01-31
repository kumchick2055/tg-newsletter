/**
 * main.js
 *
 * Bootstraps Vuetify and other plugins then mounts the App`
 */

// Plugins
import { registerPlugins } from '@/plugins'

// Components
import App from './App.vue'

// Composables
import { createPinia } from 'pinia'
import { createApp } from 'vue'

import { router } from './routers.js'
import { jwtInterceptor } from './interceptors/authInterceptor'

const pinia = createPinia()
const app = createApp(App)
app.use(pinia)
jwtInterceptor();


registerPlugins(app)

app.use(router)
app.mount('#app')
