/**
 * useApp.ts — Composable de estado global
 * ══════════════════════════════════════════════════════════════
 * Estado reactivo compartido entre todas las vistas.
 * Actúa como capa de orquestación: consume apiService y
 * expone datos listos para los componentes de presentación.
 * ══════════════════════════════════════════════════════════════
 */

import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService, type Usuario, type Formulario, type RespuestaPrevia, type RespuestaEnvio } from '../services/api.service'

const ID_FORMULARIO = 1

// Estado singleton (compartido en toda la app)
const usuario    = ref<Usuario | null>(null)
const formulario = ref<Formulario | null>(null)
const respuestasPrevias = ref<RespuestaPrevia[]>([])
const cargando   = ref(false)
const errorMsg   = ref('')

export function useApp() {
  const router = useRouter()

  // ── Inicialización ───────────────────────────────────────
  async function init() {
    try {
      await apiService.checkHealth()
    } catch {
      router.push('/error')
    }
  }

  // ── Login ────────────────────────────────────────────────
  async function identificarUsuario(nombre: string, correo: string): Promise<string | null> {
    cargando.value = true
    errorMsg.value = ''
    try {
      const data = await apiService.crearORecuperarUsuario(nombre, correo)
      usuario.value = data.usuario

      const check = await apiService.verificarUsuarioRespondio(
        data.usuario.id_usuario,
        ID_FORMULARIO
      )

      if (check.respondio) {
        await cargarRespuestasPrevias()
        router.push('/ya-respondio')
      } else {
        await cargarFormulario()
        router.push('/cuestionario')
      }
      return null
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Error desconocido'
      return msg
    } finally {
      cargando.value = false
    }
  }

  // ── Formulario ───────────────────────────────────────────
  async function cargarFormulario() {
    const data = await apiService.obtenerFormulario(ID_FORMULARIO)
    formulario.value = data.formulario
  }

  // ── Reiniciar cuestionario ──────────────────────────────
  async function reiniciarCuestionario(): Promise<string | null> {
    if (!usuario.value) return 'No hay usuario identificado'
    cargando.value = true
    errorMsg.value = ''
    try {
      await apiService.reiniciarRespuestas(
        usuario.value.id_usuario,
        ID_FORMULARIO
      )
      // Limpiar respuestas previas y estado local
      respuestasPrevias.value = []
      Object.keys(respuestasActuales).forEach(k => delete respuestasActuales[Number(k)])
      await cargarFormulario()
      router.push('/cuestionario')
      return null
    } catch (err: unknown) {
      return err instanceof Error ? err.message : 'Error al reiniciar'
    } finally {
      cargando.value = false
    }
  }

  // ── Respuestas previas ───────────────────────────────────
  async function cargarRespuestasPrevias() {
    if (!usuario.value) return
    const data = await apiService.obtenerRespuestasUsuario(
      usuario.value.id_usuario,
      ID_FORMULARIO
    )
    respuestasPrevias.value = data.respuestas
  }

  // ── Envío ────────────────────────────────────────────────
  async function enviarRespuestas(respuestas: RespuestaEnvio[]): Promise<string | null> {
    if (!usuario.value) return 'No hay usuario identificado'
    cargando.value = true
    errorMsg.value = ''
    try {
      await apiService.guardarRespuestas(
        usuario.value.id_usuario,
        ID_FORMULARIO,
        respuestas
      )
      router.push('/gracias')
      return null
    } catch (err: unknown) {
      return err instanceof Error ? err.message : 'Error al enviar'
    } finally {
      cargando.value = false
    }
  }

  // -- Ir al login (otra persona) ----------------------------
  function irALogin() {
    // Limpia solo el estado local, NO toca la base de datos
    usuario.value = null
    formulario.value = null
    respuestasPrevias.value = []
    Object.keys(respuestasActuales).forEach(k => delete respuestasActuales[Number(k)])
    errorMsg.value = ''
    router.push('/')
  }

  // ── Reintentar ───────────────────────────────────────────
  async function reintentar() {
    try {
      await apiService.checkHealth()
      router.push('/')
    } catch {
      errorMsg.value = 'El servidor sigue sin responder. Verifica que esté corriendo.'
    }
  }

  // ── Progreso del cuestionario ────────────────────────────
  const respuestasActuales = reactive<Record<number, RespuestaEnvio>>({})

  const totalPreguntas = computed(() => formulario.value?.preguntas.length ?? 0)
  const preguntasRespondidas = computed(() => {
    if (!formulario.value) return 0
    return formulario.value.preguntas.filter(p => {
      const r = respuestasActuales[p.id_pregunta]
      if (!r) return false
      if (p.tipo === 'texto_corto' || p.tipo === 'texto_largo') return !!r.respuesta_texto?.trim()
      if (p.tipo === 'escala') return r.respuesta_numero !== undefined && r.respuesta_numero !== null
      if (p.tipo === 'opcion_unica' || p.tipo === 'opcion_multiple') return (r.opciones?.length ?? 0) > 0
      return false
    }).length
  })
  const progresoPct = computed(() =>
    totalPreguntas.value > 0
      ? Math.round((preguntasRespondidas.value / totalPreguntas.value) * 100)
      : 0
  )

  return {
    // estado
    usuario,
    formulario,
    respuestasPrevias,
    cargando,
    errorMsg,
    respuestasActuales,
    // computed
    totalPreguntas,
    preguntasRespondidas,
    progresoPct,
    // acciones
    init,
    identificarUsuario,
    enviarRespuestas,
    reintentar,
    reiniciarCuestionario,
    irALogin,
  }
}
