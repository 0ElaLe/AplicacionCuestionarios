<script setup lang="ts">
import { useApp } from '../composables/useApp'

const { respuestasPrevias, irALogin } = useApp()

function formatearRespuesta(r: typeof respuestasPrevias.value[0]): string {
  if (r.respuesta_texto) return r.respuesta_texto
  if (r.respuesta_numero !== null && r.respuesta_numero !== undefined)
    return String(r.respuesta_numero)
  if (r.respuesta_fecha) return r.respuesta_fecha
  if (r.opciones_seleccionadas?.length)
    return r.opciones_seleccionadas.map(o => o.texto).join(', ')
  return '—'
}
</script>

<template>
  <div class="container--narrow view-inner">
    <div class="state-card state-card--info">
      <div class="state-icon" aria-hidden="true">📋</div>
      <h1 class="state-title">Ya respondiste este cuestionario</h1>
      <p class="state-body">
        Este correo ya tiene respuestas registradas.
        Puedes consultar lo que enviaste o permitir que otra persona responda.
      </p>

      <!-- Respuestas previas -->
      <div v-if="respuestasPrevias.length" class="respuestas-previas">
        <div
          v-for="(r, i) in respuestasPrevias"
          :key="r.id_respuesta"
          class="respuesta-previa-item"
        >
          <p class="respuesta-previa-pregunta">{{ i + 1 }}. {{ r.pregunta }}</p>
          <p class="respuesta-previa-valor">{{ formatearRespuesta(r) }}</p>
        </div>
      </div>

      <!-- Separador visual -->
      <div class="divider" />

      <!-- Aviso informativo -->
      <div class="aviso-box">
        <p class="aviso-texto">
          👤 ¿Eres otra persona? Regresa al inicio e ingresa un correo diferente.
        </p>
      </div>

      <!-- Botón para otra persona -->
      <button
        id="btn-otra-persona"
        class="btn btn--primary"
        @click="irALogin"
      >
        ← Responder como otra persona
      </button>
    </div>
  </div>
</template>

<style scoped>
.divider {
  width: 100%;
  height: 1px;
  background: var(--color-border);
  margin: var(--space-2) 0;
}

.aviso-box {
  width: 100%;
  background: var(--color-accent-light);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-md);
  padding: var(--space-4) var(--space-5);
}

.aviso-texto {
  font-size: var(--font-size-sm);
  color: var(--color-accent);
  font-weight: 500;
  line-height: 1.5;
  text-align: left;
}
</style>
