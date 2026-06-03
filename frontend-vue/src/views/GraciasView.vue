<script setup lang="ts">
import { useApp } from '../composables/useApp'

const { irALogin } = useApp()
</script>

<template>
  <div class="container--narrow view-inner">
    <div class="state-card state-card--success">
      <div class="state-icon" aria-hidden="true">✅</div>
      <h1 class="state-title">¡Gracias por tu participación!</h1>
      <p class="state-body">
        Tus respuestas han sido enviadas correctamente.
        El equipo del IIMAS-UNAM agradece tu tiempo.
      </p>

      <button
        id="btn-otra-persona"
        class="btn btn--secondary"
        @click="irALogin"
      >
        ← Permitir que otra persona responda
      </button>
    </div>
  </div>
</template>
