<script setup lang="ts">
import type { OpcionRespuesta } from '../../services/api.service'

defineProps<{
  idPregunta: number
  opciones: OpcionRespuesta[]
}>()

// v-model recibe el valor numérico seleccionado (1-5)
const model = defineModel<number | null>({ default: null })

function seleccionar(valor: number) {
  model.value = valor
}
</script>

<template>
  <div>
    <div class="scale-group" role="group" aria-label="Escala de calificación">
      <button
        v-for="opcion in opciones"
        :key="opcion.id_opcion"
        type="button"
        class="scale-btn"
        :class="{ 'is-selected': model === Number(opcion.valor) }"
        :aria-label="`Calificación ${opcion.texto}`"
        :aria-pressed="model === Number(opcion.valor)"
        @click="seleccionar(Number(opcion.valor))"
      >
        {{ opcion.texto }}
      </button>
    </div>
    <div class="scale-labels">
      <span class="scale-label-text">Mínimo</span>
      <span class="scale-label-text">Máximo</span>
    </div>
  </div>
</template>
