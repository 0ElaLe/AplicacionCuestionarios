<script setup lang="ts">
import { useApp } from '../composables/useApp'

const { reintentar, errorMsg } = useApp()
</script>

<template>
  <div class="container--narrow view-inner">
    <div class="state-card state-card--error">
      <div class="state-icon" aria-hidden="true">⚠️</div>
      <h1 class="state-title">Algo salió mal</h1>
      <p class="state-body">
        No pudimos conectar con el servidor. Verifica que el backend esté
        corriendo en <code>http://localhost:5000</code> e intenta de nuevo.
      </p>
      <p v-if="errorMsg" class="field-error" style="margin-top: 0.5rem;">{{ errorMsg }}</p>
      <button id="btn-reintentar" class="btn btn--secondary" @click="reintentar">
        Reintentar
      </button>
    </div>
  </div>
</template>
