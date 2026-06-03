<script setup lang="ts">
import { ref } from 'vue'
import { useApp } from '../composables/useApp'

const { identificarUsuario, cargando } = useApp()

const nombre = ref('')
const correo = ref('')
const errorNombre = ref('')
const errorCorreo = ref('')
const errorGlobal = ref('')

function validarCorreo(email: string) {
  return /^[\w.-]+@[\w.-]+\.\w+$/.test(email)
}

function limpiarErrores() {
  errorNombre.value = ''
  errorCorreo.value = ''
  errorGlobal.value = ''
}

async function handleSubmit() {
  limpiarErrores()
  let valido = true

  if (!nombre.value.trim()) {
    errorNombre.value = 'El nombre es obligatorio.'
    valido = false
  }
  if (!correo.value.trim()) {
    errorCorreo.value = 'El correo es obligatorio.'
    valido = false
  } else if (!validarCorreo(correo.value.trim())) {
    errorCorreo.value = 'Ingresa un correo electrónico válido.'
    valido = false
  }
  if (!valido) return

  const err = await identificarUsuario(nombre.value.trim(), correo.value.trim())
  if (err) errorGlobal.value = err
}
</script>

<template>
  <div class="container--narrow view-inner">
    <!-- Cabecera -->
    <div class="view-header">
      <div class="step-badge">Paso 1 de 2</div>
      <h1 class="view-title">Identificación</h1>
      <p class="view-subtitle">
        Ingresa tu nombre y correo para acceder al cuestionario.
      </p>
    </div>

    <!-- Formulario -->
    <form class="card" novalidate aria-label="Formulario de identificación" @submit.prevent="handleSubmit">
      <!-- Nombre -->
      <div class="field-group">
        <label class="field-label" for="input-nombre">Nombre completo</label>
        <input
          id="input-nombre"
          v-model="nombre"
          type="text"
          class="field-input"
          :class="{ 'is-invalid': errorNombre }"
          placeholder="Ej. María García López"
          autocomplete="name"
          @input="errorNombre = ''"
        />
        <span class="field-error" role="alert">{{ errorNombre }}</span>
      </div>

      <!-- Correo -->
      <div class="field-group">
        <label class="field-label" for="input-correo">Correo electrónico</label>
        <input
          id="input-correo"
          v-model="correo"
          type="email"
          class="field-input"
          :class="{ 'is-invalid': errorCorreo }"
          placeholder="Ej. mgarcia@ciencias.unam.mx"
          autocomplete="email"
          @input="errorCorreo = ''"
        />
        <span class="field-error" role="alert">{{ errorCorreo }}</span>
      </div>

      <!-- Error global -->
      <div v-if="errorGlobal" class="alert alert--error" role="alert">
        {{ errorGlobal }}
      </div>

      <!-- Botón -->
      <button id="btn-login" type="submit" class="btn btn--primary btn--full" :disabled="cargando">
        <span v-if="!cargando">Continuar</span>
        <template v-else>
          <span class="btn-spinner" aria-hidden="true" />
          <span>Verificando…</span>
        </template>
      </button>
    </form>
  </div>
</template>
