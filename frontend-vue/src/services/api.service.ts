/**
 * api.service.ts
 * ══════════════════════════════════════════════════════════════
 * Capa de acceso a datos — completamente desacoplada de la UI.
 * Todos los métodos retornan Promises tipadas.
 * ══════════════════════════════════════════════════════════════
 */

const BASE_URL = 'http://localhost:5000'

// ── Tipos ──────────────────────────────────────────────────

export interface Usuario {
  id_usuario: number
  nombre: string
  correo: string
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
  tipo: 'texto_corto' | 'texto_largo' | 'opcion_unica' | 'opcion_multiple' | 'escala'
  orden: number
  obligatoria: number  // 1 = true, 0 = false
  opciones: OpcionRespuesta[]
}

export interface Formulario {
  id_formulario: number
  titulo: string
  descripcion: string
  estado: string
  fecha_creacion: string
  preguntas: Pregunta[]
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

// ── Helper HTTP ─────────────────────────────────────────────

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const options: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json' },
  }
  if (body !== undefined) options.body = JSON.stringify(body)

  const res = await fetch(`${BASE_URL}${path}`, options)
  const data = await res.json().catch(() => ({}))

  if (!res.ok) {
    throw new Error(data.error ?? data.mensaje ?? `Error ${res.status}`)
  }
  return data as T
}

// ── Endpoints ───────────────────────────────────────────────

export const apiService = {
  /** Verifica que el backend esté disponible */
  checkHealth() {
    return request<{ status: string; mensaje: string }>('GET', '/api/health')
  },

  /** Crea o recupera un usuario por correo */
  crearORecuperarUsuario(nombre: string, correo: string) {
    return request<{ mensaje: string; usuario: Usuario }>(
      'POST', '/api/usuarios', { nombre, correo }
    )
  },

  /** Obtiene la estructura completa de un formulario */
  obtenerFormulario(idFormulario: number) {
    return request<{ formulario: Formulario }>(
      'GET', `/api/formularios/${idFormulario}`
    )
  },

  /** Verifica si el usuario ya respondió el formulario */
  verificarUsuarioRespondio(idUsuario: number, idFormulario: number) {
    return request<{ id_usuario: number; id_formulario: number; respondio: boolean }>(
      'GET', `/api/usuarios/${idUsuario}/respondio/${idFormulario}`
    )
  },

  /** Guarda las respuestas del usuario */
  guardarRespuestas(
    idUsuario: number,
    idFormulario: number,
    respuestas: RespuestaEnvio[]
  ) {
    return request<{ mensaje: string; id_intento: number }>(
      'POST', '/api/respuestas',
      { id_usuario: idUsuario, id_formulario: idFormulario, respuestas }
    )
  },

  /** Obtiene las respuestas previas de un usuario */
  obtenerRespuestasUsuario(idUsuario: number, idFormulario: number) {
    return request<{ id_usuario: number; id_formulario: number; respuestas: RespuestaPrevia[] }>(
      'GET', `/api/usuarios/${idUsuario}/respuestas/${idFormulario}`
    )
  },

  /** Elimina el intento previo para que el usuario pueda volver a responder */
  reiniciarRespuestas(idUsuario: number, idFormulario: number) {
    return request<{ mensaje: string; id_usuario: number; id_formulario: number }>(
      'DELETE', `/api/usuarios/${idUsuario}/respuestas/${idFormulario}`
    )
  },
}
