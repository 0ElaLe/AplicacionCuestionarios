<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  idPregunta: number
  obligatoria: boolean
}>()

const model = defineModel<string>({ default: '' })

const inputId = computed(() => `pregunta-${props.idPregunta}-input`)
</script>

<template>
  <div class="field-group">
    <input
      :id="inputId"
      v-model="model"
      type="text"
      class="field-input"
      placeholder="Escribe tu respuesta…"
      :required="obligatoria"
      :aria-required="obligatoria"
    />
  </div>
</template>
