import { createRouter, createWebHistory } from 'vue-router'

const TOKEN_KEY = 'iq_token'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // ── Auth ─────────────────────────────────────────────────
    { path: '/',          name: 'login',    component: () => import('../views/LoginView.vue') },
    { path: '/registro',  name: 'registro', component: () => import('../views/RegisterView.vue') },

    // ── Dashboard y flujo principal ───────────────────────────
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/crear',
      name: 'crear',
      component: () => import('../views/CrearCuestionarioView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/contestar/:codigo',
      name: 'contestar',
      component: () => import('../views/ContestarView.vue'),
    },
    {
      path: '/editar/:id',
      name: 'editar',
      component: () => import('../views/EditarCuestionarioView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/resultados/:id',
      name: 'resultados',
      component: () => import('../views/ResultadosView.vue'),
      meta: { requiresAuth: true },
    },

    // ── Flujo de respuesta ────────────────────────────────────
    { path: '/cuestionario', name: 'cuestionario', component: () => import('../views/CuestionarioView.vue') },
    { path: '/ya-respondio', name: 'ya-respondio', component: () => import('../views/YaRespondioView.vue') },
    { path: '/gracias',      name: 'gracias',      component: () => import('../views/GraciasView.vue') },
    { path: '/error',        name: 'error',        component: () => import('../views/ErrorView.vue') },
  ],
})

// Guard de autenticación
router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem(TOKEN_KEY)) {
    return { name: 'login' }
  }
})

export default router
