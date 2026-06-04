<script setup lang="ts">
/**
 * ContestarView.vue
 * Flujo completo para responder un cuestionario por código compartido.
 * - Carga el formulario, recupera avance previo
 * - Guarda automáticamente al cambiar de pregunta y al cerrar pestaña
 * - Valida respuestas obligatorias antes del envío final
 * - Muestra resultado: enviado | en_progreso | error
 */
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService, type Formulario, type Pregunta } from '../services/api.service'

// Componentes de pregunta
import TextoCortoQuestion    from '../components/questions/TextoCortoQuestion.vue'
import TextoLargoQuestion    from '../components/questions/TextoLargoQuestion.vue'
import OpcionUnicaQuestion   from '../components/questions/OpcionUnicaQuestion.vue'
import OpcionMultipleQuestion from '../components/questions/OpcionMultipleQuestion.vue'
import EscalaQuestion        from '../components/questions/EscalaQuestion.vue'
import SiNoQuestion          from '../components/questions/SiNoQuestion.vue'
import FechaQuestion         from '../components/questions/FechaQuestion.vue'

const route  = useRoute()
const router = useRouter()

const codigo   = (route.params.codigo as string).toUpperCase()
const nombre   = ref('')
const correo   = ref('')
const paso     = ref<'identificacion' | 'cuestionario' | 'gracias' | 'ya-enviado' | 'error'>('identificacion')
const formulario = ref<Formulario | null>(null)
const idUsuario  = ref<number | null>(null)
const cargando   = ref(false)
const errorMsg   = ref('')
const enviado    = ref(false)
const guardandoAvance = ref(false)

// Respuestas actuales
const respuestas = reactive<Record<number, {
  respuesta_texto?: string
  respuesta_numero?: number | null
  opciones?: number[]
}>>({})

// ── Cargar formulario ─────────────────────────────────────────
onMounted(async () => {
  try {
    const data = await apiService.obtenerFormularioPorCodigo(codigo)
    formulario.value = data.formulario
  } catch {
    paso.value = 'error'
    errorMsg.value = 'El cuestionario no existe o no está publicado.'
  }
})

// ── Identificación ────────────────────────────────────────────
async function identificarse() {
  if (!nombre.value.trim() || !correo.value.trim()) {
    errorMsg.value = 'Ingresa tu nombre y correo para continuar'
    return
  }
  cargando.value = true
  errorMsg.value = ''
  try {
    // Crear o recuperar usuario (sin contraseña — respondentes anónimos)
    const data = await apiService.crearORecuperarUsuario(nombre.value.trim(), correo.value.trim())
    idUsuario.value = data.usuario.id_usuario

    // Verificar si ya respondió
    const check = await apiService.verificarUsuarioRespondio(idUsuario.value, formulario.value!.id_formulario)
    if (check.respondio) {
      paso.value = 'ya-enviado'
      return
    }

    // Recuperar avance previo
    const avance = await apiService.obtenerAvance(idUsuario.value, formulario.value!.id_formulario)
    if (avance.estado === 'en_progreso' && avance.respuestas.length > 0) {
      avance.respuestas.forEach(r => {
        respuestas[r.id_pregunta] = {
          respuesta_texto: r.respuesta_texto ?? undefined,
          respuesta_numero: r.respuesta_numero ?? undefined,
          opciones: r.opciones ?? [],
        }
      })
    }

    paso.value = 'cuestionario'
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : 'Error al cargar el cuestionario'
  }
  cargando.value = false
}

// ── Guardado automático ───────────────────────────────────────
async function guardarAvance() {
  if (!idUsuario.value || !formulario.value) return
  guardandoAvance.value = true
  try {
    const payload = Object.entries(respuestas).map(([id, r]) => ({
      id_pregunta: Number(id),
      respuesta_texto: r.respuesta_texto ?? null,
      respuesta_numero: r.respuesta_numero ?? null,
      opciones: r.opciones ?? [],
    }))
    await apiService.guardarAvance(idUsuario.value, formulario.value.id_formulario, payload)
  } catch { /* silencioso */ }
  guardandoAvance.value = false
}

// Guardar al cerrar/salir de la pestaña
function handleBeforeUnload(e: BeforeUnloadEvent) {
  if (paso.value === 'cuestionario' && !enviado.value) {
    guardarAvance()
    e.preventDefault()
  }
}
onMounted(() => window.addEventListener('beforeunload', handleBeforeUnload))
onBeforeUnmount(() => window.removeEventListener('beforeunload', handleBeforeUnload))

// ── Validación ────────────────────────────────────────────────
const preguntasFaltantes = computed(() => {
  if (!formulario.value) return []
  return formulario.value.preguntas.filter(p => {
    if (!p.obligatoria) return false
    const r = respuestas[p.id_pregunta]
    if (!r) return true
    if (p.tipo === 'texto_corto' || p.tipo === 'texto_largo' || p.tipo === 'fecha') return !r.respuesta_texto?.trim()
    if (p.tipo === 'escala') return r.respuesta_numero === undefined || r.respuesta_numero === null
    if (p.tipo === 'opcion_unica' || p.tipo === 'opcion_multiple' || p.tipo === 'si_no') return !r.opciones?.length
    return false
  })
})

const progresoPct = computed(() => {
  if (!formulario.value?.preguntas.length) return 0
  const total = formulario.value.preguntas.length
  const respondidas = formulario.value.preguntas.filter(p => {
    const r = respuestas[p.id_pregunta]
    if (!r) return false
    if (p.tipo === 'texto_corto' || p.tipo === 'texto_largo' || p.tipo === 'fecha') return !!r.respuesta_texto?.trim()
    if (p.tipo === 'escala') return r.respuesta_numero !== null && r.respuesta_numero !== undefined
    if (p.tipo === 'opcion_unica' || p.tipo === 'opcion_multiple' || p.tipo === 'si_no') return !!r.opciones?.length
    return false
  }).length
  return Math.round((respondidas / total) * 100)
})

// ── Envío final ───────────────────────────────────────────────
async function enviar() {
  if (preguntasFaltantes.value.length > 0) {
    errorMsg.value = `Completa las preguntas obligatorias antes de enviar (${preguntasFaltantes.value.length} pendientes)`
    return
  }
  cargando.value = true
  errorMsg.value = ''
  try {
    // Construir payload respetando el tipo de cada pregunta
    const preguntaMap = Object.fromEntries(
      (formulario.value?.preguntas ?? []).map(p => [p.id_pregunta, p.tipo])
    )

    const payload = Object.entries(respuestas)
      .map(([idStr, r]) => {
        const id_pregunta = Number(idStr)
        const tipo = preguntaMap[id_pregunta]
        if (!tipo) return null

        if (tipo === 'texto_corto' || tipo === 'texto_largo' || tipo === 'fecha') {
          return { id_pregunta, respuesta_texto: r.respuesta_texto ?? '' }
        }
        if (tipo === 'escala') {
          return { id_pregunta, respuesta_numero: r.respuesta_numero ?? null }
        }
        if (tipo === 'opcion_unica' || tipo === 'opcion_multiple' || tipo === 'si_no') {
          return { id_pregunta, opciones: r.opciones ?? [] }
        }
        return null
      })
      .filter(Boolean)

    await apiService.guardarRespuestas(idUsuario.value!, formulario.value!.id_formulario, payload as any)
    enviado.value = true
    paso.value = 'gracias'
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : 'Error al enviar las respuestas'
  }
  cargando.value = false
}

// Guardar avance al cambiar respuesta
function onRespuestaChange() {
  if (paso.value === 'cuestionario' && !enviado.value) {
    // Debounce ligero
    clearTimeout((window as any)._avanceTimeout)
    ;(window as any)._avanceTimeout = setTimeout(() => guardarAvance(), 800)
  }
}
</script>

<template>
  <!-- Error de carga -->
  <div v-if="paso === 'error'" class="container--narrow view-inner">
    <div class="state-card state-card--error">
      <div class="state-icon">⚠️</div>
      <h1 class="state-title">Cuestionario no disponible</h1>
      <p class="state-body">{{ errorMsg }}</p>
      <button class="btn btn--secondary" @click="router.push('/')">← Inicio</button>
    </div>
  </div>

  <!-- Ya respondió -->
  <div v-else-if="paso === 'ya-enviado'" class="container--narrow view-inner">
    <div class="state-card state-card--info">
      <div class="state-icon">📋</div>
      <h1 class="state-title">Ya respondiste este cuestionario</h1>
      <p class="state-body">Tus respuestas ya fueron registradas anteriormente. ¡Gracias por tu participación!</p>
    </div>
  </div>

  <!-- Gracias -->
  <div v-else-if="paso === 'gracias'" class="container--narrow view-inner">
    <div class="state-card state-card--success">
      <div class="state-icon">✅</div>
      <h1 class="state-title">¡Gracias por tu participación!</h1>
      <p class="state-body">Tus respuestas han sido enviadas y registradas correctamente.</p>
    </div>
  </div>

  <!-- Cuestionario cargando -->
  <div v-else-if="!formulario" class="container--narrow view-inner">
    <div class="state-card">
      <div class="state-icon">⏳</div>
      <p class="state-body">Cargando cuestionario…</p>
    </div>
  </div>

  <!-- Identificación -->
  <div v-else-if="paso === 'identificacion'" class="container--narrow view-inner">
    <div class="contest-card">
      <h1 class="contest-titulo">{{ formulario.titulo }}</h1>
      <p v-if="formulario.descripcion" class="contest-desc">{{ formulario.descripcion }}</p>

      <hr class="divider" />

      <h2 class="contest-sub">¿Quién eres?</h2>
      <p class="contest-sub-desc">Ingresa tus datos para registrar tus respuestas.</p>

      <div class="form-group">
        <label class="form-label" for="nombre-contest">Nombre completo</label>
        <input id="nombre-contest" v-model="nombre" type="text" class="form-control"
          placeholder="Tu nombre" @keyup.enter="identificarse" />
      </div>
      <div class="form-group">
        <label class="form-label" for="correo-contest">Correo electrónico</label>
        <input id="correo-contest" v-model="correo" type="email" class="form-control"
          placeholder="ejemplo@correo.com" @keyup.enter="identificarse" />
      </div>

      <div v-if="errorMsg" class="alert alert--error">{{ errorMsg }}</div>

      <button id="btn-empezar" class="btn btn--primary" style="width:100%"
        :disabled="cargando" @click="identificarse">
        <span v-if="!cargando">Empezar cuestionario →</span>
        <template v-else><span class="btn-spinner" /><span>Cargando...</span></template>
      </button>
    </div>
  </div>

  <!-- Preguntas -->
  <div v-else class="container view-inner">
    <!-- Progreso -->
    <div class="progreso-bar">
      <div class="progreso-info">
        <span class="progreso-label">Progreso</span>
        <span class="progreso-pct">{{ progresoPct }}%</span>
      </div>
      <div class="progreso-track">
        <div class="progreso-fill" :style="{ width: progresoPct + '%' }" />
      </div>
      <span v-if="guardandoAvance" class="guardando-label">💾 Guardando...</span>
    </div>

    <h1 class="contest-titulo">{{ formulario.titulo }}</h1>

    <!-- Preguntas -->
    <div class="preguntas-form">
      <div
        v-for="(pregunta, i) in formulario.preguntas"
        :key="pregunta.id_pregunta"
        class="pregunta-block"
      >
        <div class="pregunta-encabezado">
          <span class="pregunta-numero">{{ i + 1 }}</span>
          <p class="pregunta-texto">
            {{ pregunta.texto }}
            <span v-if="pregunta.obligatoria" class="obligatoria-badge">*</span>
          </p>
        </div>

        <div class="pregunta-respuesta">
          <template v-if="pregunta.tipo === 'texto_corto'">
            <TextoCortoQuestion
              :id-pregunta="pregunta.id_pregunta"
              :model-value="respuestas[pregunta.id_pregunta]?.respuesta_texto ?? ''"
              @update:model-value="v => { respuestas[pregunta.id_pregunta] = { ...respuestas[pregunta.id_pregunta], respuesta_texto: v }; onRespuestaChange() }"
            />
          </template>
          <template v-else-if="pregunta.tipo === 'texto_largo'">
            <TextoLargoQuestion
              :id-pregunta="pregunta.id_pregunta"
              :model-value="respuestas[pregunta.id_pregunta]?.respuesta_texto ?? ''"
              @update:model-value="v => { respuestas[pregunta.id_pregunta] = { ...respuestas[pregunta.id_pregunta], respuesta_texto: v }; onRespuestaChange() }"
            />
          </template>
          <template v-else-if="pregunta.tipo === 'opcion_unica'">
            <OpcionUnicaQuestion
              :id-pregunta="pregunta.id_pregunta"
              :opciones="pregunta.opciones"
              :model-value="respuestas[pregunta.id_pregunta]?.opciones?.[0] ?? null"
              @update:model-value="v => { respuestas[pregunta.id_pregunta] = { ...respuestas[pregunta.id_pregunta], opciones: v !== null ? [v] : [] }; onRespuestaChange() }"
            />
          </template>
          <template v-else-if="pregunta.tipo === 'opcion_multiple'">
            <OpcionMultipleQuestion
              :id-pregunta="pregunta.id_pregunta"
              :opciones="pregunta.opciones"
              :model-value="respuestas[pregunta.id_pregunta]?.opciones ?? []"
              @update:model-value="v => { respuestas[pregunta.id_pregunta] = { ...respuestas[pregunta.id_pregunta], opciones: v }; onRespuestaChange() }"
            />
          </template>
          <template v-else-if="pregunta.tipo === 'escala'">
            <EscalaQuestion
              :id-pregunta="pregunta.id_pregunta"
              :opciones="pregunta.opciones"
              :model-value="respuestas[pregunta.id_pregunta]?.respuesta_numero ?? null"
              @update:model-value="v => { respuestas[pregunta.id_pregunta] = { ...respuestas[pregunta.id_pregunta], respuesta_numero: v }; onRespuestaChange() }"
            />
          </template>
          <template v-else-if="pregunta.tipo === 'si_no'">
            <SiNoQuestion
              :id-pregunta="pregunta.id_pregunta"
              :opciones="pregunta.opciones"
              :model-value="respuestas[pregunta.id_pregunta]?.opciones?.[0] ?? null"
              @update:model-value="v => { respuestas[pregunta.id_pregunta] = { ...respuestas[pregunta.id_pregunta], opciones: v !== null ? [v] : [] }; onRespuestaChange() }"
            />
          </template>
          <template v-else-if="pregunta.tipo === 'fecha'">
            <FechaQuestion
              :id-pregunta="pregunta.id_pregunta"
              :model-value="respuestas[pregunta.id_pregunta]?.respuesta_texto ?? ''"
              @update:model-value="v => { respuestas[pregunta.id_pregunta] = { ...respuestas[pregunta.id_pregunta], respuesta_texto: v }; onRespuestaChange() }"
            />
          </template>
        </div>
      </div>
    </div>

    <!-- Error y envío -->
    <div v-if="errorMsg" class="alert alert--error">{{ errorMsg }}</div>

    <button id="btn-enviar" class="btn btn--primary" style="width:100%; margin-top: var(--space-4)"
      :disabled="cargando" @click="enviar">
      <span v-if="!cargando">Enviar respuestas ✓</span>
      <template v-else><span class="btn-spinner" /><span>Enviando...</span></template>
    </button>
  </div>
</template>

<style scoped>
.contest-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-8);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  box-shadow: 0 4px 24px rgba(0,0,0,.06);
}
.contest-titulo { font-size: var(--font-size-2xl); font-weight: 700; color: var(--color-text); margin: 0; }
.contest-desc { font-size: var(--font-size-sm); color: var(--color-text-muted); margin: 0; line-height: 1.6; }
.contest-sub { font-size: var(--font-size-lg); font-weight: 700; color: var(--color-text); margin: 0; }
.contest-sub-desc { font-size: var(--font-size-sm); color: var(--color-text-muted); margin: 0; }
.divider { border: none; border-top: 1px solid var(--color-border); margin: 0; }

.progreso-bar {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  margin-bottom: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.progreso-info { display: flex; justify-content: space-between; align-items: center; }
.progreso-label { font-size: var(--font-size-xs); font-weight: 600; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: .05em; }
.progreso-pct { font-size: var(--font-size-sm); font-weight: 700; color: var(--color-primary); }
.progreso-track { height: 6px; background: var(--color-border); border-radius: 9999px; overflow: hidden; }
.progreso-fill { height: 100%; background: var(--color-primary); border-radius: 9999px; transition: width .3s ease; }
.guardando-label { font-size: var(--font-size-xs); color: var(--color-text-muted); }

.preguntas-form { display: flex; flex-direction: column; gap: var(--space-5); }
.pregunta-block {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.pregunta-encabezado { display: flex; gap: var(--space-3); align-items: flex-start; padding: var(--space-5); border-bottom: 1px solid var(--color-border); }
.pregunta-numero {
  min-width: 28px; height: 28px;
  background: var(--color-primary);
  color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--font-size-xs); font-weight: 700; flex-shrink: 0;
}
.pregunta-texto { font-size: var(--font-size-base); font-weight: 600; color: var(--color-text); margin: 0; line-height: 1.5; }
.obligatoria-badge { color: var(--color-error); margin-left: 2px; }
.pregunta-respuesta { padding: var(--space-5); }
</style>
