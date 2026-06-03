import { createRouter, createWebHistory } from 'vue-router'
import LoginView       from '../views/LoginView.vue'
import CuestionarioView from '../views/CuestionarioView.vue'
import YaRespondioView  from '../views/YaRespondioView.vue'
import GraciasView      from '../views/GraciasView.vue'
import ErrorView        from '../views/ErrorView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',            component: LoginView,        name: 'login' },
    { path: '/cuestionario', component: CuestionarioView, name: 'cuestionario' },
    { path: '/ya-respondio', component: YaRespondioView,  name: 'ya-respondio' },
    { path: '/gracias',      component: GraciasView,      name: 'gracias' },
    { path: '/error',        component: ErrorView,        name: 'error' },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

export default router
