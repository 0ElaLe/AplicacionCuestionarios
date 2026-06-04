<script setup lang="ts">
defineProps<{ idPregunta: number }>()
const model = defineModel<string>({ default: '' })
</script>

<template>
  <input
    type="date"
    class="form-control fecha-input"
    :value="model"
    @input="model = ($event.target as HTMLInputElement).value"
  />
</template>

<style scoped>
.fecha-input { max-width: 220px; }
</style>
