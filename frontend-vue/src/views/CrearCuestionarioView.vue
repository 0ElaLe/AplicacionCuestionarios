<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { apiService, type PreguntaNueva } from '../services/api.service'

const router = useRouter()
const { usuarioActual } = useAuth()

const titulo      = ref('')
const descripcion = ref('')
const visibilidad = ref('publico')
const preguntas   = ref<PreguntaNueva[]>([])
const cargando    = ref(false)
const errorMsg    = ref('')
const codigoGenerado = ref('')

const TIPOS = [
  { valor: 'texto_corto',    etiqueta: 'Texto corto' },
  { valor: 'texto_largo',    etiqueta: 'Texto largo' },
  { valor: 'opcion_unica',   etiqueta: 'Opción única' },
  { valor: 'opcion_multiple', etiqueta: 'Opción múltiple' },
  { valor: 'escala',         etiqueta: 'Escala (1–5)' },
]

function agregarPregunta() {
  preguntas.value.push({ tipo: 'texto_corto', texto: '', obligatoria: true, opciones: [] })
}

function eliminarPregunta(i: number) {
  preguntas.value.splice(i, 1)
}

function agregarOpcion(pregunta: PreguntaNueva) {
  pregunta.opciones.push({ texto: '', valor: '' })
}

function eliminarOpcion(pregunta: PreguntaNueva, i: number) {
  pregunta.opciones.splice(i, 1)
}

const conOpciones = (tipo: string) =>
  tipo === 'opcion_unica' || tipo === 'opcion_multiple'

const formValido = computed(() => {
  if (!titulo.value.trim()) return false
  if (preguntas.value.length === 0) return false
  return preguntas.value.every(p => {
    if (!p.texto.trim()) return false
    if (conOpciones(p.tipo) && p.opciones.filter(o => o.texto.trim()).length < 2) return false
    return true
  })
})

async function crear() {
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
    const data = await apiService.crearFormulario(
      titulo.value.trim(),
      descripcion.value.trim(),
      visibilidad.value,
      payload
    )
    codigoGenerado.value = data.codigo_compartir
  } catch (e: unknown) {
    errorMsg.value = e instanceof Error ? e.message : 'Error al crear el cuestionario'
  }
  cargando.value = false
}

function copiarCodigo() {
  navigator.clipboard.writeText(codigoGenerado.value)
}
</script>

<template>
  <!-- ── Éxito: mostrar código ────────────────────────────── -->
  <div v-if="codigoGenerado" class="container--narrow view-inner">
    <div class="state-card state-card--success">
      <div class="state-icon">🎉</div>
      <h1 class="state-title">¡Cuestionario creado!</h1>
      <p class="state-body">Comparte este código para que otros puedan responderlo:</p>

      <div class="codigo-display">
        <span class="codigo-texto">{{ codigoGenerado }}</span>
        <button id="btn-copiar-codigo" class="btn btn--ghost btn--sm" @click="copiarCodigo">
          📋 Copiar
        </button>
      </div>

      <button id="btn-volver-dashboard" class="btn btn--primary" @click="router.push('/dashboard')">
        ← Volver al panel
      </button>
    </div>
  </div>

  <!-- ── Formulario de creación ────────────────────────────── -->
  <div v-else class="crear-page">
    <div class="crear-header">
      <button class="btn btn--ghost btn--sm" @click="router.push('/dashboard')">← Panel</button>
      <h1 class="crear-titulo">Nuevo cuestionario</h1>
    </div>

    <div class="crear-body">
      <!-- Metadata -->
      <section class="crear-section">
        <div class="form-group">
          <label class="form-label" for="titulo">Título del cuestionario *</label>
          <input id="titulo" v-model="titulo" type="text" class="form-control"
            placeholder="Ej: Encuesta de satisfacción académica" />
        </div>
        <div class="form-group">
          <label class="form-label" for="descripcion">Descripción (opcional)</label>
          <textarea id="descripcion" v-model="descripcion" class="form-control" rows="2"
            placeholder="Instrucciones o contexto del cuestionario" />
        </div>

        <div class="form-group">
          <label class="form-label">Visibilidad</label>
          <div style="display: flex; gap: var(--space-4);">
            <label class="toggle-label">
              <input v-model="visibilidad" type="radio" value="publico" />
              🌐 Público (Aparecerá en Explorar)
            </label>
            <label class="toggle-label">
              <input v-model="visibilidad" type="radio" value="privado" />
              🔒 Privado (Solo con código)
            </label>
          </div>
        </div>
      </section>

      <!-- Preguntas -->
      <section class="crear-section">
        <h2 class="section-label">Preguntas</h2>

        <div v-if="preguntas.length === 0" class="preguntas-vacio">
          Agrega tu primera pregunta para empezar
        </div>

        <div class="preguntas-lista">
          <div
            v-for="(p, i) in preguntas"
            :key="i"
            class="pregunta-card"
          >
            <div class="pregunta-header">
              <span class="pregunta-num">Pregunta {{ i + 1 }}</span>
              <button class="btn btn--ghost btn--sm btn--danger"
                @click="eliminarPregunta(i)">✕ Eliminar</button>
            </div>

            <div class="pregunta-body">
              <div class="pregunta-row">
                <div class="form-group" style="flex:1">
                  <label class="form-label">Texto de la pregunta *</label>
                  <input v-model="p.texto" type="text" class="form-control"
                    placeholder="¿Qué deseas preguntar?" />
                </div>
                <div class="form-group" style="width: 180px">
                  <label class="form-label">Tipo</label>
                  <select v-model="p.tipo" class="form-control"
                    @change="p.opciones = []">
                    <option v-for="t in TIPOS" :key="t.valor" :value="t.valor">
                      {{ t.etiqueta }}
                    </option>
                  </select>
                </div>
                <div class="form-group" style="width: 120px; justify-content: flex-end; padding-top: 1.5rem;">
                  <label class="toggle-label">
                    <input v-model="p.obligatoria" type="checkbox" />
                    Obligatoria
                  </label>
                </div>
              </div>

              <!-- Opciones (opcion_unica / opcion_multiple) -->
              <div v-if="conOpciones(p.tipo)" class="opciones-lista">
                <label class="form-label">Opciones (mínimo 2) *</label>
                <div v-for="(op, j) in p.opciones" :key="j" class="opcion-row">
                  <input v-model="op.texto" type="text" class="form-control"
                    :placeholder="`Opción ${j + 1}`" />
                  <button class="btn btn--ghost btn--sm" @click="eliminarOpcion(p, j)">✕</button>
                </div>
                <button class="btn btn--ghost btn--sm" @click="agregarOpcion(p)">
                  + Agregar opción
                </button>
              </div>
            </div>
          </div>
        </div>

        <button id="btn-agregar-pregunta" class="btn btn--secondary"
          style="width:100%; margin-top: var(--space-3)"
          @click="agregarPregunta">
          + Agregar pregunta
        </button>
      </section>

      <!-- Error -->
      <div v-if="errorMsg" class="alert alert--error">{{ errorMsg }}</div>

      <!-- Acción -->
      <button id="btn-crear-cuestionario"
        class="btn btn--primary"
        style="width:100%"
        :disabled="!formValido || cargando"
        @click="crear"
      >
        <span v-if="!cargando">Crear cuestionario</span>
        <template v-else>
          <span class="btn-spinner" />
          <span>Creando...</span>
        </template>
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
.pregunta-card {
  background: var(--color-surface); border: 1px solid var(--color-border);
  border-radius: var(--radius-lg); overflow: hidden;
}
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
.codigo-display {
  display: flex; align-items: center; gap: var(--space-3);
  background: var(--color-bg); border: 2px solid var(--color-primary);
  border-radius: var(--radius-lg); padding: var(--space-4) var(--space-5); width: 100%;
}
.codigo-texto { font-family: monospace; font-size: 1.5rem; font-weight: 800; letter-spacing: .2em; color: var(--color-primary); flex: 1; text-align: center; }
</style>
