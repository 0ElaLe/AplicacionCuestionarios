/**
 * question.component.js
 * ══════════════════════════════════════════════════════════════
 * Componente puro de presentación para renderizar preguntas.
 * NO contiene lógica de estado ni llamadas a la API.
 *
 * Uso:
 *   const html = QuestionComponent.render(pregunta, index);
 *   container.innerHTML += html;
 * ══════════════════════════════════════════════════════════════
 */

(function (global) {
  'use strict';

  const QuestionComponent = {

    /**
     * Renderiza una pregunta completa como cadena HTML.
     * @param {Object} pregunta  - Objeto pregunta del backend.
     * @param {number} index     - Índice 0-based para numeración.
     * @returns {string} HTML string.
     */
    render(pregunta, index) {
      const numero    = index + 1;
      const esOblTop  = pregunta.obligatoria === 1;
      const idBase    = `pregunta-${pregunta.id_pregunta}`;

      const cuerpo = this._renderCuerpo(pregunta, idBase);

      return /* html */`
        <div
          class="pregunta-card"
          data-id="${pregunta.id_pregunta}"
          data-tipo="${pregunta.tipo}"
          data-obligatoria="${esOblTop ? '1' : '0'}"
          role="group"
          aria-labelledby="${idBase}-label"
          id="card-${idBase}"
        >
          <div class="pregunta-header">
            <span class="pregunta-numero" aria-hidden="true">${numero}</span>
            <p class="pregunta-texto" id="${idBase}-label">
              ${this._escapeHtml(pregunta.texto)}
              ${esOblTop
                ? '<span class="pregunta-obligatoria-badge" aria-label="obligatoria">*</span>'
                : ''}
            </p>
          </div>

          <div class="pregunta-body">
            ${cuerpo}
          </div>

          <span class="pregunta-error" id="${idBase}-error" role="alert" aria-live="polite">
            Este campo es obligatorio.
          </span>
        </div>
      `;
    },

    // ── Renderizadores por tipo ─────────────────────────────────

    _renderCuerpo(pregunta, idBase) {
      switch (pregunta.tipo) {
        case 'texto_corto':
          return this._renderTextoCorto(pregunta, idBase);
        case 'texto_largo':
          return this._renderTextoLargo(pregunta, idBase);
        case 'opcion_unica':
          return this._renderOpcionUnica(pregunta, idBase);
        case 'opcion_multiple':
          return this._renderOpcionMultiple(pregunta, idBase);
        case 'escala':
          return this._renderEscala(pregunta, idBase);
        default:
          return `<p class="field-error">Tipo de pregunta no soportado: ${pregunta.tipo}</p>`;
      }
    },

    _renderTextoCorto(pregunta, idBase) {
      return /* html */`
        <div class="field-group">
          <input
            type="text"
            id="${idBase}-input"
            class="field-input"
            name="pregunta_${pregunta.id_pregunta}"
            placeholder="Escribe tu respuesta…"
            ${pregunta.obligatoria ? 'required aria-required="true"' : ''}
            aria-describedby="${idBase}-error"
          />
        </div>
      `;
    },

    _renderTextoLargo(pregunta, idBase) {
      return /* html */`
        <div class="field-group">
          <textarea
            id="${idBase}-input"
            class="field-textarea"
            name="pregunta_${pregunta.id_pregunta}"
            placeholder="Escribe tu respuesta…"
            rows="4"
            ${pregunta.obligatoria ? 'required aria-required="true"' : ''}
            aria-describedby="${idBase}-error"
          ></textarea>
        </div>
      `;
    },

    _renderOpcionUnica(pregunta, idBase) {
      const items = pregunta.opciones.map(opcion => /* html */`
        <label class="choice-item" for="${idBase}-opcion-${opcion.id_opcion}">
          <input
            type="radio"
            id="${idBase}-opcion-${opcion.id_opcion}"
            name="pregunta_${pregunta.id_pregunta}"
            value="${opcion.id_opcion}"
            ${pregunta.obligatoria ? 'required aria-required="true"' : ''}
          />
          <span class="choice-label">${this._escapeHtml(opcion.texto)}</span>
        </label>
      `).join('');

      return `<div class="choice-group" role="radiogroup">${items}</div>`;
    },

    _renderOpcionMultiple(pregunta, idBase) {
      const items = pregunta.opciones.map(opcion => /* html */`
        <label class="choice-item" for="${idBase}-opcion-${opcion.id_opcion}">
          <input
            type="checkbox"
            id="${idBase}-opcion-${opcion.id_opcion}"
            name="pregunta_${pregunta.id_pregunta}"
            value="${opcion.id_opcion}"
          />
          <span class="choice-label">${this._escapeHtml(opcion.texto)}</span>
        </label>
      `).join('');

      return `<div class="choice-group">${items}</div>`;
    },

    _renderEscala(pregunta, idBase) {
      const opciones = pregunta.opciones.length > 0
        ? pregunta.opciones
        : [
            { id_opcion: null, valor: '1', texto: '1' },
            { id_opcion: null, valor: '2', texto: '2' },
            { id_opcion: null, valor: '3', texto: '3' },
            { id_opcion: null, valor: '4', texto: '4' },
            { id_opcion: null, valor: '5', texto: '5' },
          ];

      const botones = opciones.map(op => /* html */`
        <button
          type="button"
          class="scale-btn"
          data-value="${op.valor || op.texto}"
          data-id="${pregunta.id_pregunta}"
          aria-label="Calificación ${op.texto}"
          aria-pressed="false"
        >${this._escapeHtml(op.texto)}</button>
      `).join('');

      return /* html */`
        <div>
          <div class="scale-group" role="group" aria-label="Escala de calificación" id="${idBase}-scale">
            ${botones}
          </div>
          <div class="scale-labels">
            <span class="scale-label-text">Mínimo</span>
            <span class="scale-label-text">Máximo</span>
          </div>
          <input
            type="hidden"
            id="${idBase}-hidden"
            name="pregunta_${pregunta.id_pregunta}"
            value=""
            ${pregunta.obligatoria ? 'required' : ''}
          />
        </div>
      `;
    },

    // ── Renderizador de respuesta previa (vista de solo lectura) ─

    /**
     * Renderiza una respuesta previa del usuario (read-only).
     * @param {Object} respuesta - Objeto respuesta del backend.
     * @param {number} index
     * @returns {string} HTML string.
     */
    renderPreviewer(respuesta, index) {
      const valor = this._extractValorRespuesta(respuesta);
      return /* html */`
        <div class="respuesta-previa-item">
          <p class="respuesta-previa-pregunta">${index + 1}. ${this._escapeHtml(respuesta.pregunta)}</p>
          <p class="respuesta-previa-valor">${this._escapeHtml(valor)}</p>
        </div>
      `;
    },

    _extractValorRespuesta(respuesta) {
      if (respuesta.respuesta_texto) return respuesta.respuesta_texto;
      if (respuesta.respuesta_numero !== null && respuesta.respuesta_numero !== undefined) {
        return String(respuesta.respuesta_numero);
      }
      if (respuesta.respuesta_fecha) return respuesta.respuesta_fecha;
      if (respuesta.opciones_seleccionadas && respuesta.opciones_seleccionadas.length > 0) {
        return respuesta.opciones_seleccionadas.map(o => o.texto).join(', ');
      }
      return '—';
    },

    // ── Utilidades ───────────────────────────────────────────────

    _escapeHtml(str) {
      if (typeof str !== 'string') return String(str ?? '');
      return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;');
    },
  };

  global.QuestionComponent = QuestionComponent;
})(window);
