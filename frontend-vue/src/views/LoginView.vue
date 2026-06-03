<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const correo   = ref('')
const password = ref('')
const cargando = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  if (!correo.value || !password.value) {
    errorMsg.value = 'Completa todos los campos'
    return
  }
  cargando.value = true
  errorMsg.value = ''
  const err = await login(correo.value.trim(), password.value)
  cargando.value = false
  if (err) {
    errorMsg.value = err
  } else {
    router.push('/dashboard')
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-logo">
        <img src="/logo.png" alt="Logo IIMAS-UNAM" class="auth-logo-img" />
      </div>

      <h1 class="auth-title">Iniciar sesión</h1>
      <p class="auth-subtitle">Bienvenido al sistema de cuestionarios</p>

      <form class="auth-form" @submit.prevent="handleLogin" novalidate>
        <div class="form-group">
          <label class="form-label" for="correo">Correo electrónico</label>
          <input
            id="correo"
            v-model="correo"
            type="email"
            class="form-control"
            placeholder="ejemplo@correo.com"
            autocomplete="email"
            required
          />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </div>

        <div v-if="errorMsg" class="alert alert--error" role="alert">
          {{ errorMsg }}
        </div>

        <button
          id="btn-login"
          type="submit"
          class="btn btn--primary"
          style="width:100%"
          :disabled="cargando"
        >
          <span v-if="!cargando">Entrar</span>
          <template v-else>
            <span class="btn-spinner" aria-hidden="true" />
            <span>Verificando...</span>
          </template>
        </button>
      </form>

      <p class="auth-footer">
        ¿No tienes cuenta?
        <router-link to="/registro" class="auth-link">Regístrate aquí</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg);
  padding: var(--space-6);
}

.auth-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-5);
  box-shadow: 0 4px 24px rgba(0,0,0,.06);
}

.auth-logo { display: flex; justify-content: center; }
.auth-logo-img { height: 64px; object-fit: contain; }

.auth-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
  text-align: center;
}

.auth-subtitle {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
  text-align: center;
}

.auth-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.auth-footer {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  text-align: center;
  margin: 0;
}

.auth-link {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}
.auth-link:hover { text-decoration: underline; }
</style>
