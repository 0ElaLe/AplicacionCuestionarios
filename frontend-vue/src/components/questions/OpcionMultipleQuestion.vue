<script setup lang="ts">
import type { OpcionRespuesta } from '../../services/api.service'

defineProps<{
  idPregunta: number
  opciones: OpcionRespuesta[]
}>()

// v-model recibe array de id_opcion seleccionados
const model = defineModel<number[]>({ default: () => [] })
</script>

<template>
  <div class="choice-group">
    <label
      v-for="opcion in opciones"
      :key="opcion.id_opcion"
      class="choice-item"
      :class="{ 'is-selected': model.includes(opcion.id_opcion) }"
      :for="`pregunta-${idPregunta}-opcion-${opcion.id_opcion}`"
    >
      <input
        :id="`pregunta-${idPregunta}-opcion-${opcion.id_opcion}`"
        v-model="model"
        type="checkbox"
        class="choice-checkbox"
        :value="opcion.id_opcion"
      />
      <span class="choice-label">{{ opcion.texto }}</span>
    </label>
  </div>
</template>
