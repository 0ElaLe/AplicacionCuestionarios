<script setup lang="ts">
import type { OpcionRespuesta } from '../../services/api.service'

defineProps<{
  idPregunta: number
  opciones: OpcionRespuesta[]
  obligatoria: boolean
}>()

// v-model recibe el id_opcion seleccionado (number | null)
const model = defineModel<number | null>({ default: null })
</script>

<template>
  <div class="choice-group" role="radiogroup">
    <label
      v-for="opcion in opciones"
      :key="opcion.id_opcion"
      class="choice-item"
      :class="{ 'is-selected': model === opcion.id_opcion }"
      :for="`pregunta-${idPregunta}-opcion-${opcion.id_opcion}`"
    >
      <input
        :id="`pregunta-${idPregunta}-opcion-${opcion.id_opcion}`"
        v-model="model"
        type="radio"
        class="choice-radio"
        :value="opcion.id_opcion"
        :name="`pregunta-${idPregunta}`"
      />
      <span class="choice-label">{{ opcion.texto }}</span>
    </label>
  </div>
</template>
