/**
 * api.service.ts
 * ══════════════════════════════════════════════════════════════
 * Capa de acceso a datos — completamente desacoplada de la UI.
 * ══════════════════════════════════════════════════════════════
 */

const BASE_URL = 'http://localhost:5000'
const TOKEN_KEY = 'iq_token'

// ── Tipos ──────────────────────────────────────────────────

export interface Usuario {
  id_usuario: number
  nombre: string
  correo: string
  rol: string
  fecha_creacion: string
}

export interface OpcionRespuesta {
  id_opcion: number
  texto: string
  valor: string
  orden: number
}

export interface Pregunta {
  id_pregunta: number
  texto: string
  tipo: 'texto_corto' | 'texto_largo' | 'opcion_unica' | 'opcion_multiple' | 'escala' | 'si_no' | 'fecha'
  orden: number
  obligatoria: number
  opciones: OpcionRespuesta[]
}

export interface ResultadoPregunta {
  id_pregunta: number
  texto: string
  tipo: string
  orden: number
  obligatoria: number
  // texto/fecha
  respuestas_texto?: string[]
  // escala
  promedio?: number | null
  distribucion?: Record<string, number>
  total?: number
  // opciones
  opciones?: { id_opcion: number; texto: string; conteo: number; porcentaje: number }[]
}

export interface ResultadosFormulario {
  formulario: { id_formulario: number; titulo: string; descripcion: string }
  total_respuestas: number
  preguntas: ResultadoPregunta[]
}

export interface Formulario {
  id_formulario: number
  titulo: string
  descripcion: string
  estado: string
  codigo_compartir?: string
  fecha_creacion: string
  preguntas: Pregunta[]
}

export interface FormularioResumen {
  id_formulario: number
  titulo: string
  descripcion: string
  estado: string
  codigo_compartir: string
  fecha_creacion: string
  visibilidad?: string
}

export interface FormularioPublico {
  id_formulario: number
  titulo: string
  descripcion: string
  codigo_compartir: string
  fecha_creacion: string
  creado_por: string | null
  total_preguntas: number
  total_respuestas: number
}

export interface FormularioRespondido {
  id_formulario: number
  titulo: string
  descripcion: string
  codigo_compartir: string
  fecha_intento: string
  creado_por: string | null
  total_preguntas: number
  preguntas_respondidas: number
}


export interface RespuestaEnvio {
  id_pregunta: number
  respuesta_texto?: string
  respuesta_numero?: number
  opciones?: number[]
}

export interface RespuestaPrevia {
  id_respuesta: number
  id_pregunta: number
  pregunta: string
  tipo: string
  respuesta_texto: string | null
  respuesta_numero: number | null
  respuesta_fecha: string | null
  opciones_seleccionadas: { id_opcion: number; texto: string; valor: string }[]
}

export interface PreguntaNueva {
  tipo: string
  texto: string
  obligatoria: boolean
  opciones: { texto: string; valor?: string }[]
}

export interface AvanceRespuesta {
  id_pregunta: number
  respuesta_texto?: string | null
  respuesta_numero?: number | null
  opciones?: number[]
}

// ── Helper HTTP ─────────────────────────────────────────────

function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) headers['Authorization'] = `Bearer ${token}`
  return headers
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const options: RequestInit = { method, headers: getHeaders() }
  if (body !== undefined) options.body = JSON.stringify(body)
  const res = await fetch(`${BASE_URL}${path}`, options)
  const data = await res.json().catch(() => ({}))
  if (!res.ok) throw new Error(data.error ?? data.mensaje ?? `Error ${res.status}`)
  return data as T
}

// ── Endpoints ───────────────────────────────────────────────

export const apiService = {

  // ── Health ──────────────────────────────────────────────────
  checkHealth() {
    return request<{ status: string; mensaje: string }>('GET', '/api/health')
  },

  // ── Auth v2 ─────────────────────────────────────────────────
  registro(nombre: string, correo: string, password: string) {
    return request<{ token: string; usuario: Usuario }>(
      'POST', '/api/auth/registro', { nombre, correo, password }
    )
  },

  login(correo: string, password: string) {
    return request<{ token: string; usuario: Usuario }>(
      'POST', '/api/auth/login', { correo, password }
    )
  },

  meProfile() {
    return request<{ usuario: Usuario }>('GET', '/api/auth/me')
  },

  // ── Formularios v2 ───────────────────────────────────────────
  crearFormulario(titulo: string, descripcion: string, visibilidad: string, preguntas: PreguntaNueva[]) {
    return request<{ id_formulario: number; codigo_compartir: string }>(
      'POST', '/api/v2/formularios', { titulo, descripcion, visibilidad, preguntas }
    )
  },

  obtenerFormularioPorCodigo(codigo: string) {
    return request<{ formulario: Formulario }>('GET', `/api/v2/formularios/codigo/${codigo}`)
  },

  misFormularios() {
    return request<{ formularios: FormularioResumen[] }>('GET', '/api/v2/formularios/mios')
  },

  formulariosPublicos() {
    return request<{ formularios: FormularioPublico[] }>('GET', '/api/v2/formularios/publicos')
  },

  formulariosRespondidos(idUsuario: number) {
    return request<{ formularios: FormularioRespondido[] }>('GET', `/api/v2/formularios/respondidos/${idUsuario}`)
  },


  // ── Avance v2 ────────────────────────────────────────────────
  guardarAvance(idUsuario: number, idFormulario: number, respuestas: AvanceRespuesta[]) {
    return request<{ mensaje: string; ya_enviado: boolean }>(
      'POST', '/api/v2/avance',
      { id_usuario: idUsuario, id_formulario: idFormulario, respuestas }
    )
  },

  obtenerAvance(idUsuario: number, idFormulario: number) {
    return request<{ estado: string | null; respuestas: AvanceRespuesta[] }>(
      'GET', `/api/v2/avance/${idUsuario}/${idFormulario}`
    )
  },

  obtenerFormularioPorId(idFormulario: number) {
    return request<{ formulario: Formulario }>('GET', `/api/v2/formularios/${idFormulario}`)
  },

  editarFormulario(idFormulario: number, titulo: string, descripcion: string, visibilidad: string, preguntas: PreguntaNueva[]) {
    return request<{ preguntas_editadas: boolean; tiene_respuestas: boolean }>(
      'PUT', `/api/v2/formularios/${idFormulario}`, { titulo, descripcion, visibilidad, preguntas }
    )
  },

  archivarFormulario(idFormulario: number) {
    return request<{ estado: string }>('PATCH', `/api/v2/formularios/${idFormulario}/archivar`)
  },

  obtenerResultados(idFormulario: number) {
    return request<ResultadosFormulario>('GET', `/api/v2/formularios/${idFormulario}/resultados`)
  },

  // ── Legacy (flujo original) ───────────────────────────────────
  crearORecuperarUsuario(nombre: string, correo: string) {
    return request<{ mensaje: string; usuario: Usuario }>(
      'POST', '/api/usuarios', { nombre, correo }
    )
  },

  obtenerFormulario(idFormulario: number) {
    return request<{ formulario: Formulario }>('GET', `/api/formularios/${idFormulario}`)
  },

  verificarUsuarioRespondio(idUsuario: number, idFormulario: number) {
    return request<{ id_usuario: number; id_formulario: number; respondio: boolean }>(
      'GET', `/api/usuarios/${idUsuario}/respondio/${idFormulario}`
    )
  },

  guardarRespuestas(idUsuario: number, idFormulario: number, respuestas: RespuestaEnvio[]) {
    return request<{ mensaje: string; id_intento: number }>(
      'POST', '/api/respuestas',
      { id_usuario: idUsuario, id_formulario: idFormulario, respuestas }
    )
  },

  obtenerRespuestasUsuario(idUsuario: number, idFormulario: number) {
    return request<{ id_usuario: number; id_formulario: number; respuestas: RespuestaPrevia[] }>(
      'GET', `/api/usuarios/${idUsuario}/respuestas/${idFormulario}`
    )
  },
}
