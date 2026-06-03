/**
 * api.service.js
 * ══════════════════════════════════════════════════════════════
 * Capa de acceso a datos (Service Layer)
 * Completamente desacoplada de la UI.
 * Todos los métodos retornan Promises.
 *
 * Uso:
 *   const svc = ApiService('http://localhost:5000');
 *   const usuario = await svc.crearORecuperarUsuario('Ana', 'ana@unam.mx');
 * ══════════════════════════════════════════════════════════════
 */

(function (global) {
  'use strict';

  /**
   * Fábrica del servicio de API.
   * @param {string} baseUrl - URL base del backend (sin slash al final).
   * @returns {Object} Objeto con métodos del servicio.
   */
  function ApiService(baseUrl) {
    const BASE = (baseUrl || 'http://localhost:5000').replace(/\/$/, '');

    // ── Helper interno: fetch con JSON ──────────────────────────
    async function _request(method, path, body) {
      const options = {
        method,
        headers: { 'Content-Type': 'application/json' },
      };

      if (body !== undefined) {
        options.body = JSON.stringify(body);
      }

      const response = await fetch(`${BASE}${path}`, options);
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const errorMsg =
          data.error ||
          data.mensaje ||
          `Error ${response.status}: ${response.statusText}`;
        throw new Error(errorMsg);
      }

      return data;
    }

    // ── Endpoints públicos ──────────────────────────────────────

    /**
     * Verifica que el backend esté en línea.
     * @returns {Promise<{ status: string, mensaje: string }>}
     */
    async function checkHealth() {
      return _request('GET', '/api/health');
    }

    /**
     * Crea o recupera un usuario por correo electrónico.
     * @param {string} nombre
     * @param {string} correo
     * @returns {Promise<{ mensaje: string, usuario: Object }>}
     */
    async function crearORecuperarUsuario(nombre, correo) {
      return _request('POST', '/api/usuarios', { nombre, correo });
    }

    /**
     * Obtiene la estructura completa de un formulario.
     * @param {number} idFormulario
     * @returns {Promise<{ formulario: Object }>}
     */
    async function obtenerFormulario(idFormulario) {
      return _request('GET', `/api/formularios/${idFormulario}`);
    }

    /**
     * Verifica si un usuario ya respondió un formulario.
     * @param {number} idUsuario
     * @param {number} idFormulario
     * @returns {Promise<{ id_usuario: number, id_formulario: number, respondio: boolean }>}
     */
    async function verificarUsuarioRespondio(idUsuario, idFormulario) {
      return _request(
        'GET',
        `/api/usuarios/${idUsuario}/respondio/${idFormulario}`
      );
    }

    /**
     * Guarda las respuestas de un usuario.
     * @param {number} idUsuario
     * @param {number} idFormulario
     * @param {Array}  respuestas
     * @returns {Promise<{ mensaje: string, id_intento: number }>}
     */
    async function guardarRespuestas(idUsuario, idFormulario, respuestas) {
      return _request('POST', '/api/respuestas', {
        id_usuario: idUsuario,
        id_formulario: idFormulario,
        respuestas,
      });
    }

    /**
     * Obtiene las respuestas previas de un usuario para un formulario.
     * @param {number} idUsuario
     * @param {number} idFormulario
     * @returns {Promise<{ id_usuario: number, id_formulario: number, respuestas: Array }>}
     */
    async function obtenerRespuestasUsuario(idUsuario, idFormulario) {
      return _request(
        'GET',
        `/api/usuarios/${idUsuario}/respuestas/${idFormulario}`
      );
    }

    // ── API pública del servicio ────────────────────────────────
    return {
      checkHealth,
      crearORecuperarUsuario,
      obtenerFormulario,
      verificarUsuarioRespondio,
      guardarRespuestas,
      obtenerRespuestasUsuario,
    };
  }

  // Exportar al scope global
  global.ApiService = ApiService;
})(window);
