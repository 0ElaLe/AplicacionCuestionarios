<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiService, type PreguntaNueva } from '../services/api.service'

const router = useRouter()
const route  = useRoute()
const id = Number(route.params.id)

const titulo      = ref('')
const descripcion = ref('')
const visibilidad = ref('publico')
const preguntas   = ref<PreguntaNueva[]>([])
const cargando    = ref(false)
const cargandoInicial = ref(true)
const errorMsg    = ref('')
const exito       = ref(false)
const tieneRespuestas = ref(false)

const TIPOS = [
  { valor: 'texto_corto',     etiqueta: 'Texto corto' },
  { valor: 'texto_largo',     etiqueta: 'Texto largo' },
  { valor: 'opcion_unica',    etiqueta: 'Opción única' },
  { valor: 'opcion_multiple', etiqueta: 'Opción múltiple' },
  { valor: 'escala',          etiqueta: 'Escala (1–5)' },
  { valor: 'si_no',           etiqueta: 'Sí / No' },
  { valor: 'fecha',           etiqueta: 'Fecha' },
]

onMounted(async () => {
  try {
    const data = await apiService.obtenerFormularioPorId(id)
    const f = data.formulario
    titulo.value      = f.titulo
    descripcion.value = f.descripcion ?? ''
    visibilidad.value = (f as any).visibilidad ?? 'publico'
    preguntas.value   = f.preguntas.map(p => ({
      tipo: p.tipo,
      texto: p.texto,
      obligatoria: Boolean(p.obligatoria),
      opciones: (p.tipo === 'si_no')
        ? []   // si_no no muestra opciones en el editor
        : p.opciones.map(o => ({ texto: o.texto, valor: o.valor })),
    }))
    // Check if it has responses by trying to get resultados
    try {
      const res = await apiService.obtenerResultados(id)
      tieneRespuestas.value = res.total_respuestas > 0
    } catch { /* ignore */ }
  } catch {
    errorMsg.value = 'No se pudo cargar el cuestionario.'
  }
  cargandoInicial.value = false
})

function agregarPregunta() {
  preguntas.value.push({ tipo: 'texto_corto', texto: '', obligatoria: true, opciones: [] })
}
function eliminarPregunta(i: number) {
  preguntas.value.splice(i, 1)
}
function subirPregunta(i: number) {
  if (i === 0) return
  const arr = preguntas.value
  ;[arr[i - 1], arr[i]] = [arr[i], arr[i - 1]]
}
function bajarPregunta(i: number) {
  if (i === preguntas.value.length - 1) return
  const arr = preguntas.value
  ;[arr[i], arr[i + 1]] = [arr[i + 1], arr[i]]
}
function agregarOpcion(p: PreguntaNueva) {
  p.opciones.push({ texto: '', valor: '' })
}
function eliminarOpcion(p: PreguntaNueva, i: number) {
  p.opciones.splice(i, 1)
}

const conOpciones = (tipo: string) => tipo === 'opcion_unica' || tipo === 'opcion_multiple'

const formValido = computed(() => {
  if (!titulo.value.trim()) return false
  if (preguntas.value.length === 0) return false
  return preguntas.value.every(p => {
    if (!p.texto.trim()) return false
    if (conOpciones(p.tipo) && p.opciones.filter(o => o.texto.trim()).length < 2) return false
    return true
  })
})

async function guardar() {
  if (!formValido.value) {
    errorMsg.value = 'Revisa que todas las preguntas tengan texto y al menos 2 opciones donde aplique'
    return
  }
  cargando.value = true
  errorMsg.value = ''
  try {
    const payload = preguntas.value.map(p => ({
      ...p,
      opciones: conOpciones(p.tipo) ? p.opciones.filter(o => o.texto.trim()) : [],
    }))
    await apiService.editarFormulario(id, titulo.value.trim(), descripcion.value.trim(), visibilidad.value, payload)
    exito.value = true
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : 'Error al guardar los cambios'
  }
  cargando.value = false
}
</script>

<template>
  <div v-if="exito" class="container--narrow view-inner">
    <div class="state-card state-card--success">
      <div class="state-icon">✅</div>
      <h1 class="state-title">¡Cambios guardados!</h1>
      <p class="state-body">El cuestionario ha sido actualizado correctamente.</p>
      <button class="btn btn--primary" @click="router.push('/dashboard')">← Volver al panel</button>
    </div>
  </div>

  <div v-else-if="cargandoInicial" class="container--narrow view-inner">
    <div class="state-card"><p class="state-body">Cargando cuestionario…</p></div>
  </div>

  <div v-else class="crear-page">
    <div class="crear-header">
      <button class="btn btn--ghost btn--sm" @click="router.push('/dashboard')">← Panel</button>
      <h1 class="crear-titulo">Editar cuestionario</h1>
    </div>

    <div class="crear-body">
      <!-- Aviso si tiene respuestas -->
      <div v-if="tieneRespuestas" class="alert alert--warn">
        ⚠️ Este cuestionario ya tiene respuestas. Solo puedes editar el título, descripción y visibilidad.
      </div>

      <section class="crear-section">
        <div class="form-group">
          <label class="form-label">Título *</label>
          <input v-model="titulo" type="text" class="form-control" placeholder="Título del cuestionario" />
        </div>
        <div class="form-group">
          <label class="form-label">Descripción</label>
          <textarea v-model="descripcion" class="form-control" rows="2" placeholder="Instrucciones o contexto" />
        </div>
        <div class="form-group">
          <label class="form-label">Visibilidad</label>
          <div style="display:flex;gap:var(--space-4);">
            <label class="toggle-label"><input v-model="visibilidad" type="radio" value="publico" /> 🌐 Público</label>
            <label class="toggle-label"><input v-model="visibilidad" type="radio" value="privado" /> 🔒 Privado</label>
          </div>
        </div>
      </section>

      <!-- Preguntas (solo si no hay respuestas) -->
      <section v-if="!tieneRespuestas" class="crear-section">
        <h2 class="section-label">Preguntas</h2>

        <div v-if="preguntas.length === 0" class="preguntas-vacio">Agrega tu primera pregunta</div>

        <div class="preguntas-lista">
          <div v-for="(p, i) in preguntas" :key="i" class="pregunta-card">
            <div class="pregunta-header">
              <span class="pregunta-num">Pregunta {{ i + 1 }}</span>
              <div style="display:flex;gap:var(--space-2);align-items:center;">
                <button class="btn btn--ghost btn--sm" :disabled="i === 0" @click="subirPregunta(i)">↑</button>
                <button class="btn btn--ghost btn--sm" :disabled="i === preguntas.length - 1" @click="bajarPregunta(i)">↓</button>
                <button class="btn btn--ghost btn--sm btn--danger" @click="eliminarPregunta(i)">✕ Eliminar</button>
              </div>
            </div>
            <div class="pregunta-body">
              <div class="pregunta-row">
                <div class="form-group" style="flex:1">
                  <label class="form-label">Texto *</label>
                  <input v-model="p.texto" type="text" class="form-control" placeholder="¿Qué deseas preguntar?" />
                </div>
                <div class="form-group" style="width:180px">
                  <label class="form-label">Tipo</label>
                  <select v-model="p.tipo" class="form-control" @change="p.opciones = []">
                    <option v-for="t in TIPOS" :key="t.valor" :value="t.valor">{{ t.etiqueta }}</option>
                  </select>
                </div>
                <div class="form-group" style="width:120px;justify-content:flex-end;padding-top:1.5rem;">
                  <label class="toggle-label"><input v-model="p.obligatoria" type="checkbox" /> Obligatoria</label>
                </div>
              </div>

              <div v-if="conOpciones(p.tipo)" class="opciones-lista">
                <label class="form-label">Opciones (mínimo 2) *</label>
                <div v-for="(op, j) in p.opciones" :key="j" class="opcion-row">
                  <input v-model="op.texto" type="text" class="form-control" :placeholder="`Opción ${j + 1}`" />
                  <button class="btn btn--ghost btn--sm" @click="eliminarOpcion(p, j)">✕</button>
                </div>
                <button class="btn btn--ghost btn--sm" @click="agregarOpcion(p)">+ Agregar opción</button>
              </div>
              <div v-else-if="p.tipo === 'si_no'" class="tipo-preview">
                <span class="tipo-preview-badge">👍 Sí</span>
                <span class="tipo-preview-badge">👎 No</span>
              </div>
              <div v-else-if="p.tipo === 'fecha'" class="tipo-preview">
                <span class="tipo-preview-badge">📅 Selector de fecha</span>
              </div>
              <div v-else-if="p.tipo === 'escala'" class="tipo-preview">
                <span class="tipo-preview-badge">⭐ Escala del 1 al 5</span>
              </div>
            </div>
          </div>
        </div>

        <button class="btn btn--secondary" style="width:100%;margin-top:var(--space-3)" @click="agregarPregunta">
          + Agregar pregunta
        </button>
      </section>

      <div v-if="errorMsg" class="alert alert--error">{{ errorMsg }}</div>

      <button class="btn btn--primary" style="width:100%" :disabled="!formValido || cargando" @click="guardar">
        <span v-if="!cargando">Guardar cambios</span>
        <template v-else><span class="btn-spinner" /><span>Guardando...</span></template>
      </button>
    </div>
  </div>
</template>

<style scoped>
.crear-page { min-height: 100vh; background: var(--color-bg); }
.crear-header {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-4) var(--space-8);
  background: var(--color-surface); border-bottom: 1px solid var(--color-border);
}
.crear-titulo { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-text); margin: 0; }
.crear-body {
  max-width: 780px; margin: 0 auto;
  padding: var(--space-8) var(--space-6);
  display: flex; flex-direction: column; gap: var(--space-6);
}
.crear-section { display: flex; flex-direction: column; gap: var(--space-4); }
.section-label { font-size: var(--font-size-lg); font-weight: 700; color: var(--color-text); margin: 0; }
.preguntas-vacio {
  padding: var(--space-6); text-align: center;
  color: var(--color-text-muted); font-size: var(--font-size-sm);
  border: 1px dashed var(--color-border); border-radius: var(--radius-lg);
}
.preguntas-lista { display: flex; flex-direction: column; gap: var(--space-4); }
.pregunta-card { background: var(--color-surface); border: 1px solid var(--color-border); border-radius: var(--radius-lg); overflow: hidden; }
.pregunta-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--space-3) var(--space-5);
  background: var(--color-bg); border-bottom: 1px solid var(--color-border);
}
.pregunta-num { font-size: var(--font-size-xs); font-weight: 700; color: var(--color-text-muted); text-transform: uppercase; letter-spacing: .05em; }
.pregunta-body { padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); }
.pregunta-row { display: flex; gap: var(--space-3); align-items: flex-start; flex-wrap: wrap; }
.toggle-label { display: flex; align-items: center; gap: var(--space-2); font-size: var(--font-size-sm); color: var(--color-text-muted); cursor: pointer; white-space: nowrap; }
.opciones-lista { display: flex; flex-direction: column; gap: var(--space-2); }
.opcion-row { display: flex; gap: var(--space-2); align-items: center; }
.btn--danger { color: var(--color-error); }
.tipo-preview { display: flex; gap: var(--space-3); flex-wrap: wrap; }
.tipo-preview-badge {
  font-size: var(--font-size-sm); color: var(--color-text-muted);
  background: var(--color-bg); border: 1px dashed var(--color-border);
  border-radius: var(--radius-md); padding: var(--space-2) var(--space-4);
}
.alert--warn {
  background: #fffbeb; border: 1px solid #fcd34d;
  color: #92400e; border-radius: var(--radius-lg); padding: var(--space-4) var(--space-5);
  font-size: var(--font-size-sm);
}
</style>
