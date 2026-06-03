import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './assets/main.css'
// Google Fonts — Inter
const link = document.createElement('link')
link.rel = 'stylesheet'
link.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap'
document.head.appendChild(link)

createApp(App).use(router).mount('#app')
