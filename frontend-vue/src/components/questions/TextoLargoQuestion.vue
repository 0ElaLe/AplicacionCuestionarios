<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  idPregunta: number
  obligatoria: boolean
}>()

const model = defineModel<string>({ default: '' })
const textareaId = computed(() => `pregunta-${props.idPregunta}-input`)
</script>

<template>
  <div class="field-group">
    <textarea
      :id="textareaId"
      v-model="model"
      class="field-textarea"
      placeholder="Escribe tu respuesta…"
      rows="4"
      :required="obligatoria"
    />
  </div>
</template>
