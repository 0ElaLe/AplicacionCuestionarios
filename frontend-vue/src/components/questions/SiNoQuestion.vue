<script setup lang="ts">
import type { OpcionRespuesta } from '../../services/api.service'

defineProps<{
  idPregunta: number
  opciones: OpcionRespuesta[]
}>()

// v-model: id_opcion seleccionado (o null)
const model = defineModel<number | null>({ default: null })
</script>

<template>
  <div class="sino-group" role="group">
    <button
      v-for="opcion in opciones"
      :key="opcion.id_opcion"
      type="button"
      class="sino-btn"
      :class="{
        'is-selected': model === opcion.id_opcion,
        'sino-btn--si': opcion.valor === 'si',
        'sino-btn--no': opcion.valor === 'no',
      }"
      @click="model = opcion.id_opcion"
    >
      <span class="sino-icon">{{ opcion.valor === 'si' ? '👍' : '👎' }}</span>
      <span class="sino-label">{{ opcion.texto }}</span>
    </button>
  </div>
</template>

<style scoped>
.sino-group { display: flex; gap: var(--space-4); }

.sino-btn {
  flex: 1;
  display: flex; flex-direction: column; align-items: center; gap: var(--space-2);
  padding: var(--space-5) var(--space-4);
  background: var(--color-bg);
  border: 2px solid var(--color-border);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: border-color .15s, background .15s, transform .1s;
  font-family: inherit;
}
.sino-btn:hover { border-color: #bbbbd0; transform: translateY(-1px); }
.sino-btn.is-selected.sino-btn--si  { border-color: #22c55e; background: #f0fdf4; }
.sino-btn.is-selected.sino-btn--no  { border-color: #ef4444; background: #fef2f2; }
.sino-icon { font-size: 1.8rem; }
.sino-label { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text); }
</style>
