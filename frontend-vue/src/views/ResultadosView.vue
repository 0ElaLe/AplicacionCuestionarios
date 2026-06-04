<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { apiService, type ResultadosFormulario, type ResultadoPregunta } from '../services/api.service'

const router = useRouter()
const route  = useRoute()
const id = Number(route.params.id)

const datos    = ref<ResultadosFormulario | null>(null)
const cargando = ref(true)
const errorMsg = ref('')

onMounted(async () => {
  try {
    datos.value = await apiService.obtenerResultados(id)
  } catch {
    errorMsg.value = 'No se pudieron cargar los resultados.'
  }
  cargando.value = false
})

function etiquetaTipo(tipo: string) {
  const mapa: Record<string, string> = {
    texto_corto: 'Texto corto', texto_largo: 'Texto largo',
    opcion_unica: 'Opción única', opcion_multiple: 'Opción múltiple',
    escala: 'Escala', si_no: 'Sí / No', fecha: 'Fecha',
  }
  return mapa[tipo] ?? tipo
}

function maxConteo(p: ResultadoPregunta) {
  if (!p.opciones?.length) return 1
  return Math.max(...p.opciones.map(o => o.conteo), 1)
}
</script>

<template>
  <div class="res-page">
    <header class="res-header">
      <button class="btn btn--ghost btn--sm" @click="router.push('/dashboard')">← Panel</button>
      <h1 class="res-titulo">Resultados</h1>
    </header>

    <div v-if="cargando" class="res-body">
      <div class="state-card"><p class="state-body">Cargando resultados…</p></div>
    </div>

    <div v-else-if="errorMsg" class="res-body">
      <div class="state-card state-card--error"><p class="state-body">{{ errorMsg }}</p></div>
    </div>

    <div v-else-if="datos" class="res-body">
      <div class="res-meta">
        <h2 class="res-form-titulo">{{ datos.formulario.titulo }}</h2>
        <span class="res-badge">{{ datos.total_respuestas }} respuesta{{ datos.total_respuestas !== 1 ? 's' : '' }}</span>
      </div>

      <div v-if="datos.total_respuestas === 0" class="estado-vacio">
        Aún no hay respuestas para este cuestionario.
      </div>

      <div v-else class="preguntas-grid">
        <div v-for="(p, i) in datos.preguntas" :key="p.id_pregunta" class="res-card">
          <div class="res-card-header">
            <span class="res-num">{{ i + 1 }}</span>
            <div class="res-card-info">
              <p class="res-pregunta-texto">{{ p.texto }}</p>
              <span class="res-tipo-badge">{{ etiquetaTipo(p.tipo) }}</span>
            </div>
          </div>

          <!-- Texto / Fecha -->
          <div v-if="['texto_corto', 'texto_largo', 'fecha'].includes(p.tipo)" class="res-texto-lista">
            <div v-if="!p.respuestas_texto?.length" class="res-vacio">Sin respuestas</div>
            <div v-for="(txt, j) in p.respuestas_texto" :key="j" class="res-texto-item">
              {{ txt }}
            </div>
          </div>

          <!-- Escala -->
          <div v-else-if="p.tipo === 'escala'" class="res-escala">
            <div class="res-promedio">
              <span class="res-promedio-num">{{ p.promedio ?? '—' }}</span>
              <span class="res-promedio-label">promedio / 5</span>
            </div>
            <div class="res-dist">
              <div v-for="val in ['1','2','3','4','5']" :key="val" class="res-dist-row">
                <span class="res-dist-label">{{ val }}</span>
                <div class="res-bar-track">
                  <div
                    class="res-bar-fill"
                    :style="{ width: p.total ? ((p.distribucion?.[val] ?? 0) / p.total * 100) + '%' : '0%' }"
                  />
                </div>
                <span class="res-dist-count">{{ p.distribucion?.[val] ?? 0 }}</span>
              </div>
            </div>
          </div>

          <!-- Opción única / múltiple / Sí No -->
          <div v-else-if="['opcion_unica', 'opcion_multiple', 'si_no'].includes(p.tipo)" class="res-opciones">
            <div v-if="!p.opciones?.length" class="res-vacio">Sin opciones</div>
            <div v-for="op in p.opciones" :key="op.id_opcion" class="res-opcion-row">
              <span class="res-opcion-texto">{{ op.texto }}</span>
              <div class="res-bar-track res-bar-track--wide">
                <div
                  class="res-bar-fill"
                  :class="op.texto === 'Sí' ? 'res-bar-fill--si' : op.texto === 'No' ? 'res-bar-fill--no' : ''"
                  :style="{ width: (op.conteo / maxConteo(p) * 100) + '%' }"
                />
              </div>
              <span class="res-opcion-stat">{{ op.conteo }} ({{ op.porcentaje }}%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.res-page { min-height: 100vh; background: var(--color-bg); }

.res-header {
  display: flex; align-items: center; gap: var(--space-4);
  padding: var(--space-4) var(--space-8);
  background: var(--color-surface); border-bottom: 1px solid var(--color-border);
}
.res-titulo { font-size: var(--font-size-xl); font-weight: 700; color: var(--color-text); margin: 0; }

.res-body {
  max-width: 820px; margin: 0 auto;
  padding: var(--space-8) var(--space-6);
  display: flex; flex-direction: column; gap: var(--space-6);
}

.res-meta { display: flex; align-items: center; gap: var(--space-4); flex-wrap: wrap; }
.res-form-titulo { font-size: var(--font-size-2xl); font-weight: 700; color: var(--color-text); margin: 0; flex: 1; }
.res-badge {
  font-size: var(--font-size-sm); font-weight: 700;
  background: var(--color-primary); color: #fff;
  padding: var(--space-2) var(--space-4); border-radius: var(--radius-full);
  white-space: nowrap;
}

.estado-vacio {
  padding: var(--space-8); text-align: center;
  color: var(--color-text-muted); font-size: var(--font-size-sm);
  background: var(--color-surface); border: 1px dashed var(--color-border);
  border-radius: var(--radius-lg);
}

.preguntas-grid { display: flex; flex-direction: column; gap: var(--space-5); }

.res-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.res-card-header {
  display: flex; gap: var(--space-4); align-items: flex-start;
  padding: var(--space-5); border-bottom: 1px solid var(--color-border);
}
.res-num {
  min-width: 28px; height: 28px;
  background: var(--color-primary); color: #fff; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: var(--font-size-xs); font-weight: 700; flex-shrink: 0;
}
.res-card-info { display: flex; flex-direction: column; gap: var(--space-1); flex: 1; }
.res-pregunta-texto { font-size: var(--font-size-base); font-weight: 600; color: var(--color-text); margin: 0; }
.res-tipo-badge {
  font-size: 0.65rem; text-transform: uppercase; letter-spacing: .05em;
  background: #e4e4ec; color: var(--color-text-secondary);
  padding: 2px 8px; border-radius: var(--radius-full); align-self: flex-start;
}

/* Texto */
.res-texto-lista { padding: var(--space-4) var(--space-5); display: flex; flex-direction: column; gap: var(--space-2); max-height: 240px; overflow-y: auto; }
.res-texto-item {
  font-size: var(--font-size-sm); color: var(--color-text);
  background: var(--color-bg); border-radius: var(--radius-md);
  padding: var(--space-3) var(--space-4);
  border-left: 3px solid var(--color-primary);
}
.res-vacio { font-size: var(--font-size-sm); color: var(--color-text-muted); padding: var(--space-4); }

/* Escala */
.res-escala { padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-4); }
.res-promedio { display: flex; align-items: baseline; gap: var(--space-2); }
.res-promedio-num { font-size: 2.2rem; font-weight: 800; color: var(--color-primary); }
.res-promedio-label { font-size: var(--font-size-sm); color: var(--color-text-muted); }
.res-dist { display: flex; flex-direction: column; gap: var(--space-2); }
.res-dist-row { display: flex; align-items: center; gap: var(--space-3); }
.res-dist-label { font-size: var(--font-size-sm); font-weight: 700; color: var(--color-text-muted); width: 16px; text-align: center; }
.res-dist-count { font-size: var(--font-size-xs); color: var(--color-text-muted); width: 24px; text-align: right; }

/* Barras */
.res-bar-track {
  flex: 1; height: 10px;
  background: var(--color-border); border-radius: 9999px; overflow: hidden;
}
.res-bar-track--wide { height: 14px; }
.res-bar-fill { height: 100%; background: var(--color-primary); border-radius: 9999px; transition: width .4s ease; }
.res-bar-fill--si  { background: #22c55e; }
.res-bar-fill--no  { background: #ef4444; }

/* Opciones */
.res-opciones { padding: var(--space-5); display: flex; flex-direction: column; gap: var(--space-3); }
.res-opcion-row { display: flex; align-items: center; gap: var(--space-3); }
.res-opcion-texto { font-size: var(--font-size-sm); font-weight: 600; color: var(--color-text); min-width: 80px; }
.res-opcion-stat { font-size: var(--font-size-xs); color: var(--color-text-muted); white-space: nowrap; min-width: 70px; text-align: right; }
</style>
