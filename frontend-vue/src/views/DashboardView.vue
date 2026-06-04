<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { apiService, type FormularioResumen, type FormularioPublico, type FormularioRespondido } from '../services/api.service'
// FormularioResumen.estado puede ser 'publicado' | 'archivado'

const router = useRouter()
const { usuarioActual, logout, cargarPerfil } = useAuth()

const codigoInput   = ref('')
const errorCodigo   = ref('')
const cargandoCode  = ref(false)

const tabActual = ref<'creados' | 'respondidos' | 'publicos'>('creados')

const misFormularios = ref<FormularioResumen[]>([])
const respondidos = ref<FormularioRespondido[]>([])
const publicos = ref<FormularioPublico[]>([])

const cargandoLista = ref(false)
const copiado = ref<string | null>(null)
const archivando = ref<number | null>(null)

async function toggleArchivar(f: FormularioResumen) {
  archivando.value = f.id_formulario
  try {
    const res = await apiService.archivarFormulario(f.id_formulario)
    f.estado = res.estado
  } catch { /* ignorar */ }
  archivando.value = null
}

onMounted(async () => {
  await cargarPerfil()
  await cargarListas()
})

async function cargarListas() {
  cargandoLista.value = true
  try {
    const [misReq, respReq, pubReq] = await Promise.all([
      apiService.misFormularios(),
      apiService.formulariosRespondidos(usuarioActual.value?.id_usuario ?? 0),
      apiService.formulariosPublicos()
    ])
    misFormularios.value = misReq.formularios
    respondidos.value = respReq.formularios
    publicos.value = pubReq.formularios
  } catch { /* ignorar parciales */ }
  cargandoLista.value = false
}

async function entrarConCodigo() {
  const codigo = codigoInput.value.trim().toUpperCase()
  if (!codigo) { errorCodigo.value = 'Ingresa el código del cuestionario'; return }
  cargandoCode.value = true
  errorCodigo.value = ''
  try {
    await apiService.obtenerFormularioPorCodigo(codigo)
    router.push(`/contestar/${codigo}`)
  } catch {
    errorCodigo.value = 'Código no encontrado o cuestionario no publicado'
  }
  cargandoCode.value = false
}

function copiarCodigo(codigo: string) {
  navigator.clipboard.writeText(codigo).then(() => {
    copiado.value = codigo
    setTimeout(() => { copiado.value = null }, 2000)
  })
}
</script>

<template>
  <div class="dashboard-page">
    <!-- Header -->
    <header class="dash-header">
      <img src="/logo.png" alt="Logo" class="dash-logo" />
      <div class="dash-user">
        <span class="dash-user-name">{{ (usuarioActual as any)?.nombre ?? '...' }}</span>
        <button id="btn-logout" class="btn btn--ghost btn--sm" @click="logout">Cerrar sesión</button>
      </div>
    </header>

    <main class="dash-main">
      <h1 class="dash-title">Panel de cuestionarios</h1>

      <!-- Opciones principales -->
      <div class="dash-opciones">
        <!-- Opción A: Crear -->
        <div class="dash-card dash-card--crear">
          <div class="dash-card-icon">✏️</div>
          <h2 class="dash-card-title">Crear cuestionario</h2>
          <p class="dash-card-desc">
            Diseña tu propio cuestionario con múltiples tipos de preguntas
            y obtén un código para compartirlo.
          </p>
          <button
            id="btn-ir-crear"
            class="btn btn--primary"
            @click="router.push('/crear')"
          >
            Crear nuevo
          </button>
        </div>

        <!-- Opción B: Contestar -->
        <div class="dash-card dash-card--contestar">
          <div class="dash-card-icon">📝</div>
          <h2 class="dash-card-title">Contestar cuestionario</h2>
          <p class="dash-card-desc">
            Ingresa el código que te compartieron para acceder al cuestionario.
          </p>
          <div class="codigo-input-row">
            <input
              id="input-codigo"
              v-model="codigoInput"
              type="text"
              class="form-control codigo-input"
              placeholder="Ej: A3F9B2C1D4"
              maxlength="10"
              @keyup.enter="entrarConCodigo"
            />
            <button
              id="btn-entrar-codigo"
              class="btn btn--primary"
              :disabled="cargandoCode"
              @click="entrarConCodigo"
            >
              <span v-if="!cargandoCode">Entrar</span>
              <span v-else class="btn-spinner" />
            </button>
          </div>
          <p v-if="errorCodigo" class="codigo-error">{{ errorCodigo }}</p>
        </div>
      </div>

      <!-- Pestañas de listas -->
      <section class="listas-section">
        <div class="tabs-nav">
          <button class="tab-btn" :class="{ 'is-active': tabActual === 'creados' }" @click="tabActual = 'creados'">
            Mis creados ({{ misFormularios.length }})
          </button>
          <button class="tab-btn" :class="{ 'is-active': tabActual === 'respondidos' }" @click="tabActual = 'respondidos'">
            Historial ({{ respondidos.length }})
          </button>
          <button class="tab-btn" :class="{ 'is-active': tabActual === 'publicos' }" @click="tabActual = 'publicos'">
            Explorar públicos
          </button>
        </div>

        <div v-if="cargandoLista" class="mis-estado">Cargando datos...</div>

        <!-- Tab: Creados -->
        <div v-else-if="tabActual === 'creados'" class="tab-pane">
          <div v-if="misFormularios.length === 0" class="mis-estado mis-estado--vacio">
            Aún no has creado ningún cuestionario.
          </div>
          <div v-else class="mis-lista">
            <div v-for="f in misFormularios" :key="f.id_formulario" class="mis-item mis-item--creado">
              <div class="mis-item-info">
                <p class="mis-item-titulo">
                  {{ f.titulo }}
                  <span v-if="f.estado === 'archivado'" class="tag-archivado">Archivado</span>
                </p>
                <p class="mis-item-fecha">Creado el {{ new Date(f.fecha_creacion).toLocaleDateString('es-MX') }}</p>
              </div>
              <div class="mis-item-acciones">
                <span class="codigo-badge">{{ f.codigo_compartir }}</span>
                <button class="btn btn--ghost btn--sm" :title="copiado === f.codigo_compartir ? '¡Copiado!' : 'Copiar código'" @click="copiarCodigo(f.codigo_compartir)">
                  {{ copiado === f.codigo_compartir ? '✓' : '📋' }}
                </button>
                <button class="btn btn--ghost btn--sm" title="Ver resultados" @click="router.push(`/resultados/${f.id_formulario}`)">📊</button>
                <button class="btn btn--ghost btn--sm" title="Editar" @click="router.push(`/editar/${f.id_formulario}`)">✏️</button>
                <button class="btn btn--ghost btn--sm" :title="f.estado === 'archivado' ? 'Publicar' : 'Archivar'"
                  :disabled="archivando === f.id_formulario"
                  @click="toggleArchivar(f)">
                  {{ f.estado === 'archivado' ? '📤' : '📦' }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab: Respondidos (Historial) -->
        <div v-else-if="tabActual === 'respondidos'" class="tab-pane">
          <div v-if="respondidos.length === 0" class="mis-estado mis-estado--vacio">
            Aún no has respondido ningún cuestionario.
          </div>
          <div v-else class="mis-lista">
            <div v-for="f in respondidos" :key="f.id_formulario" class="mis-item">
              <div class="mis-item-info">
                <p class="mis-item-titulo">{{ f.titulo }}</p>
                <p class="mis-item-meta">
                  Por {{ f.creado_por || 'Anónimo' }} &bull; Respondido el {{ new Date(f.fecha_intento).toLocaleDateString('es-MX') }}
                </p>
              </div>
              <div class="mis-item-codigo">
                <span class="meta-tag">{{ f.preguntas_respondidas }} / {{ f.total_preguntas }} respondidas</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab: Públicos (Explorar) -->
        <div v-else-if="tabActual === 'publicos'" class="tab-pane">
          <div v-if="publicos.length === 0" class="mis-estado mis-estado--vacio">
            No hay cuestionarios públicos disponibles.
          </div>
          <div v-else class="mis-lista">
            <div v-for="f in publicos" :key="f.id_formulario" class="mis-item is-clickable" @click="router.push(`/contestar/${f.codigo_compartir}`)">
              <div class="mis-item-info">
                <p class="mis-item-titulo">{{ f.titulo }} <span class="tag-public">Público</span></p>
                <p class="mis-item-meta">
                  Por {{ f.creado_por || 'Anónimo' }} &bull; {{ f.total_preguntas }} preguntas &bull; {{ f.total_respuestas }} respuestas
                </p>
                <p class="mis-item-desc" v-if="f.descripcion">{{ f.descripcion }}</p>
              </div>
              <div class="mis-item-action">
                <span class="action-arrow">→</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style scoped>
.dashboard-page { min-height: 100vh; background: var(--color-bg); }

.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-8);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}
.dash-logo { height: 44px; object-fit: contain; }
.dash-user { display: flex; align-items: center; gap: var(--space-3); }
.dash-user-name { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text); }

.dash-main {
  max-width: 900px;
  margin: 0 auto;
  padding: var(--space-8) var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.dash-title { font-size: var(--font-size-2xl); font-weight: 700; color: var(--color-text); margin: 0; }

.dash-opciones {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-6);
}

.dash-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-7);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  transition: box-shadow .2s;
}
.dash-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,.08); }

.dash-card-icon { font-size: 2rem; }
.dash-card-title { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-text); margin: 0; }
.dash-card-desc { font-size: var(--font-size-sm); color: var(--color-text-muted); line-height: 1.6; margin: 0; flex: 1; }

.codigo-input-row { display: flex; gap: var(--space-2); }
.codigo-input { flex: 1; font-family: monospace; text-transform: uppercase; letter-spacing: .1em; }
.codigo-error { font-size: var(--font-size-xs); color: var(--color-error); margin: 0; }

/* Tabs */
.listas-section { display: flex; flex-direction: column; gap: var(--space-4); }
.tabs-nav {
  display: flex; gap: var(--space-4); border-bottom: 2px solid var(--color-border);
  margin-bottom: var(--space-4);
}
.tab-btn {
  background: transparent; border: none; padding: var(--space-3) 0;
  font-size: var(--font-size-sm); font-weight: 650; color: var(--color-text-muted);
  cursor: pointer; position: relative;
  transition: color var(--transition-fast);
}
.tab-btn:hover { color: var(--color-text); }
.tab-btn.is-active { color: var(--color-primary); }
.tab-btn.is-active::after {
  content: ''; position: absolute; bottom: -2px; left: 0; right: 0;
  height: 2px; background: var(--color-primary); border-radius: 2px;
}

.mis-estado { font-size: var(--font-size-sm); color: var(--color-text-muted); padding: var(--space-6); text-align: center; }
.mis-estado--vacio { background: var(--color-surface); border: 1px dashed var(--color-border); border-radius: var(--radius-lg); }

.mis-lista { display: flex; flex-direction: column; gap: var(--space-3); }
.mis-item {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-5);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  transition: box-shadow var(--transition-fast), border-color var(--transition-fast);
}
.mis-item.is-clickable { cursor: pointer; }
.mis-item.is-clickable:hover {
  border-color: #bbbbd0;
  box-shadow: 0 4px 12px rgba(0,0,0,.05);
}
.mis-item-info { display: flex; flex-direction: column; gap: var(--space-1); }
.mis-item-titulo { font-weight: 600; color: var(--color-text); font-size: var(--font-size-sm); margin: 0; display: flex; align-items: center; gap: 8px;}
.mis-item-fecha { font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 0; }
.mis-item-meta { font-size: var(--font-size-xs); color: var(--color-text-muted); margin: 0; }
.mis-item-desc { font-size: var(--font-size-xs); color: var(--color-text-secondary); margin-top: 4px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

.mis-item-codigo { display: flex; align-items: center; gap: var(--space-2); }
.mis-item-acciones { display: flex; align-items: center; gap: var(--space-2); flex-wrap: wrap; }
.tag-archivado {
  font-size: 0.65rem; text-transform: uppercase; letter-spacing: .05em;
  background: #fef3c7; color: #92400e;
  padding: 2px 6px; border-radius: 4px;
}
.codigo-badge {
  font-family: monospace;
  font-size: var(--font-size-sm);
  font-weight: 700;
  letter-spacing: .08em;
  color: var(--color-primary);
  background: var(--color-accent-light, #eff6ff);
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-sm);
}

.meta-tag {
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--color-text-secondary);
  background: #e4e4ec;
  padding: 4px 8px;
  border-radius: var(--radius-full);
}

.tag-public {
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  background: #e0f2fe;
  color: #0369a1;
  padding: 2px 6px;
  border-radius: 4px;
}

.action-arrow {
  color: var(--color-primary);
  font-size: 1.25rem;
  font-weight: bold;
}

@media (max-width: 640px) {
  .dash-opciones { grid-template-columns: 1fr; }
  .dash-header { padding: var(--space-4); }
  .tabs-nav { overflow-x: auto; white-space: nowrap; padding-bottom: 2px; }
}
</style>

