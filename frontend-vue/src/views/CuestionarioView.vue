<script setup lang="ts">
import { ref, computed } from 'vue'
import { useApp } from '../composables/useApp'
import type { RespuestaEnvio } from '../services/api.service'
import TextoCortoQuestion    from '../components/questions/TextoCortoQuestion.vue'
import TextoLargoQuestion    from '../components/questions/TextoLargoQuestion.vue'
import OpcionUnicaQuestion   from '../components/questions/OpcionUnicaQuestion.vue'
import OpcionMultipleQuestion from '../components/questions/OpcionMultipleQuestion.vue'
import EscalaQuestion        from '../components/questions/EscalaQuestion.vue'

const {
  formulario,
  cargando,
  respuestasActuales,
  totalPreguntas,
  preguntasRespondidas,
  progresoPct,
  enviarRespuestas,
} = useApp()

const errorGlobal = ref('')
const invalidas   = ref<Set<number>>(new Set())

// ── Helpers de v-model por tipo ──────────────────────────────

function getTexto(idPregunta: number) {
  return (respuestasActuales[idPregunta]?.respuesta_texto ?? '')
}
function setTexto(idPregunta: number, val: string) {
  respuestasActuales[idPregunta] = { id_pregunta: idPregunta, respuesta_texto: val }
  invalidas.value.delete(idPregunta)
}

function getOpcionUnica(idPregunta: number) {
  return respuestasActuales[idPregunta]?.opciones?.[0] ?? null
}
function setOpcionUnica(idPregunta: number, val: number | null) {
  respuestasActuales[idPregunta] = { id_pregunta: idPregunta, opciones: val !== null ? [val] : [] }
  invalidas.value.delete(idPregunta)
}

function getOpciones(idPregunta: number): number[] {
  return respuestasActuales[idPregunta]?.opciones ?? []
}
function setOpciones(idPregunta: number, val: number[]) {
  respuestasActuales[idPregunta] = { id_pregunta: idPregunta, opciones: val }
  invalidas.value.delete(idPregunta)
}

function getEscala(idPregunta: number): number | null {
  return respuestasActuales[idPregunta]?.respuesta_numero ?? null
}
function setEscala(idPregunta: number, val: number | null) {
  respuestasActuales[idPregunta] = { id_pregunta: idPregunta, respuesta_numero: val ?? undefined }
  invalidas.value.delete(idPregunta)
}

// ── Validación y envío ───────────────────────────────────────

function validar(): boolean {
  if (!formulario.value) return false
  const nuevasInvalidas = new Set<number>()

  for (const p of formulario.value.preguntas) {
    if (!p.obligatoria) continue
    const r = respuestasActuales[p.id_pregunta]
    let respondida = false

    if (p.tipo === 'texto_corto' || p.tipo === 'texto_largo') {
      respondida = !!r?.respuesta_texto?.trim()
    } else if (p.tipo === 'opcion_unica') {
      respondida = (r?.opciones?.length ?? 0) > 0
    } else if (p.tipo === 'opcion_multiple') {
      respondida = (r?.opciones?.length ?? 0) > 0
    } else if (p.tipo === 'escala') {
      respondida = r?.respuesta_numero !== undefined && r?.respuesta_numero !== null
    }

    if (!respondida) nuevasInvalidas.add(p.id_pregunta)
  }

  invalidas.value = nuevasInvalidas
  return nuevasInvalidas.size === 0
}

async function handleSubmit() {
  errorGlobal.value = ''
  if (!validar()) {
    errorGlobal.value = 'Por favor, responde todas las preguntas obligatorias (*).'
    // Scroll a primera inválida
    const firstId = [...invalidas.value][0]
    document.getElementById(`card-pregunta-${firstId}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }

  const payload: RespuestaEnvio[] = Object.values(respuestasActuales)
  const err = await enviarRespuestas(payload)
  if (err) errorGlobal.value = err
}
</script>

<template>
  <div class="container--wide view-inner">
    <!-- Cabecera del formulario -->
    <div class="cuestionario-header">
      <div class="step-badge">Paso 2 de 2</div>
      <h1 class="view-title">{{ formulario?.titulo }}</h1>
      <p class="view-subtitle">{{ formulario?.descripcion }}</p>
    </div>

    <!-- Barra de progreso -->
    <div>
      <div class="progress-wrap" aria-hidden="true">
        <div class="progress-bar" :style="{ width: progresoPct + '%' }" />
      </div>
      <p class="progress-label">{{ preguntasRespondidas }} de {{ totalPreguntas }} preguntas respondidas</p>
    </div>

    <!-- Formulario -->
    <form novalidate aria-label="Cuestionario" @submit.prevent="handleSubmit">
      <div class="preguntas-container">
        <div
          v-for="(pregunta, index) in formulario?.preguntas"
          :id="`card-pregunta-${pregunta.id_pregunta}`"
          :key="pregunta.id_pregunta"
          class="pregunta-card"
          :class="{ 'is-invalid': invalidas.has(pregunta.id_pregunta) }"
          role="group"
          :aria-labelledby="`pregunta-${pregunta.id_pregunta}-label`"
        >
          <!-- Encabezado de la pregunta -->
          <div class="pregunta-header">
            <span class="pregunta-numero" aria-hidden="true">{{ index + 1 }}</span>
            <p :id="`pregunta-${pregunta.id_pregunta}-label`" class="pregunta-texto">
              {{ pregunta.texto }}
              <span v-if="pregunta.obligatoria" class="pregunta-obligatoria" aria-label="obligatoria">*</span>
            </p>
          </div>

          <!-- Cuerpo según tipo -->
          <TextoCortoQuestion
            v-if="pregunta.tipo === 'texto_corto'"
            :id-pregunta="pregunta.id_pregunta"
            :obligatoria="!!pregunta.obligatoria"
            :model-value="getTexto(pregunta.id_pregunta)"
            @update:model-value="val => setTexto(pregunta.id_pregunta, val)"
          />
          <TextoLargoQuestion
            v-else-if="pregunta.tipo === 'texto_largo'"
            :id-pregunta="pregunta.id_pregunta"
            :obligatoria="!!pregunta.obligatoria"
            :model-value="getTexto(pregunta.id_pregunta)"
            @update:model-value="val => setTexto(pregunta.id_pregunta, val)"
          />
          <OpcionUnicaQuestion
            v-else-if="pregunta.tipo === 'opcion_unica'"
            :id-pregunta="pregunta.id_pregunta"
            :opciones="pregunta.opciones"
            :obligatoria="!!pregunta.obligatoria"
            :model-value="getOpcionUnica(pregunta.id_pregunta)"
            @update:model-value="val => setOpcionUnica(pregunta.id_pregunta, val)"
          />
          <OpcionMultipleQuestion
            v-else-if="pregunta.tipo === 'opcion_multiple'"
            :id-pregunta="pregunta.id_pregunta"
            :opciones="pregunta.opciones"
            :model-value="getOpciones(pregunta.id_pregunta)"
            @update:model-value="val => setOpciones(pregunta.id_pregunta, val)"
          />
          <EscalaQuestion
            v-else-if="pregunta.tipo === 'escala'"
            :id-pregunta="pregunta.id_pregunta"
            :opciones="pregunta.opciones"
            :model-value="getEscala(pregunta.id_pregunta)"
            @update:model-value="val => setEscala(pregunta.id_pregunta, val)"
          />

          <!-- Error de validación -->
          <p v-if="invalidas.has(pregunta.id_pregunta)" class="pregunta-error" role="alert">
            Este campo es obligatorio.
          </p>
        </div>
      </div>

      <!-- Error global -->
      <div v-if="errorGlobal" class="alert alert--error" role="alert" style="margin-top: 1.5rem;">
        {{ errorGlobal }}
      </div>

      <!-- Botón enviar -->
      <div class="form-actions">
        <button id="btn-submit" type="submit" class="btn btn--primary" :disabled="cargando">
          <span v-if="!cargando">Enviar respuestas</span>
          <template v-else>
            <span class="btn-spinner" aria-hidden="true" />
            <span>Enviando…</span>
          </template>
        </button>
      </div>
    </form>
  </div>
</template>
