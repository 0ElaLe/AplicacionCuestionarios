/**
 * app.js
 * ══════════════════════════════════════════════════════════════
 * Orquestador principal de la aplicación.
 *
 * Arquitectura:
 *   ApiService  ←── datos puros (HTTP)
 *   QuestionComponent ←── presentación pura (HTML strings)
 *   AppController ←── estado + flujo (este archivo)
 *
 * El AppController actúa como "contenedor" que une el servicio
 * de datos con los componentes de presentación.
 * ══════════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  /* ── Configuración ─────────────────────────────────────── */
  const CONFIG = {
    API_BASE_URL:  'http://localhost:5000',
    ID_FORMULARIO: 1,
  };

  /* ── Estado de la aplicación (modelo de estado) ─────────── */
  const state = {
    usuario:      null,   // { id_usuario, nombre, correo }
    formulario:   null,   // { id_formulario, titulo, descripcion, preguntas[] }
    cargando:     false,
  };

  /* ── Referencias al DOM ─────────────────────────────────── */
  const $ = id => document.getElementById(id);

  const dom = {
    views: {
      login:       $('view-login'),
      cuestionario: $('view-cuestionario'),
      yaRespondio: $('view-ya-respondio'),
      gracias:     $('view-gracias'),
      error:       $('view-error'),
    },
    login: {
      form:        $('form-login'),
      inputNombre: $('input-nombre'),
      inputCorreo: $('input-correo'),
      errorNombre: $('error-nombre'),
      errorCorreo: $('error-correo'),
      errorGlobal: $('login-error-global'),
      btnSubmit:   $('btn-login'),
    },
    cuestionario: {
      form:            $('form-cuestionario'),
      tituloFormulario: $('titulo-formulario'),
      descFormulario:  $('descripcion-formulario'),
      preguntasContainer: $('preguntas-container'),
      errorGlobal:     $('cuestionario-error-global'),
      btnSubmit:       $('btn-submit'),
      progressBar:     $('progress-bar'),
      progressLabel:   $('progress-label'),
    },
    yaRespondio: {
      container: $('respuestas-previas-container'),
    },
    error: {
      message:   $('error-message'),
      btnReintentar: $('btn-reintentar'),
    },
  };

  /* ── Instanciar el servicio de API ──────────────────────── */
  const api = ApiService(CONFIG.API_BASE_URL);

  /* ══════════════════════════════════════════════════════════
     ROUTER — Manejo de vistas
  ══════════════════════════════════════════════════════════ */

  function showView(viewName) {
    Object.values(dom.views).forEach(v => {
      v.classList.remove('view--active');
    });

    const target = dom.views[viewName];
    if (target) {
      target.classList.add('view--active');
      // Reiniciar la animación
      target.style.animation = 'none';
      void target.offsetWidth;
      target.style.animation = '';
    }
  }

  /* ══════════════════════════════════════════════════════════
     FLUJO PRINCIPAL
  ══════════════════════════════════════════════════════════ */

  async function init() {
    // 1. Verificar que el backend esté disponible
    try {
      await api.checkHealth();
    } catch {
      mostrarError(
        'No se pudo conectar con el servidor. ' +
        'Verifica que el backend esté corriendo en ' +
        `<code>${CONFIG.API_BASE_URL}</code>.`
      );
      return;
    }

    // 2. Mostrar vista de login
    showView('login');

    // 3. Registrar eventos
    dom.login.form.addEventListener('submit', handleLoginSubmit);
    dom.cuestionario.form.addEventListener('submit', handleCuestionarioSubmit);
    dom.error.btnReintentar.addEventListener('click', () => {
      showView('login');
    });
  }

  /* ── PASO 1: Login ──────────────────────────────────────── */

  async function handleLoginSubmit(e) {
    e.preventDefault();

    if (!validarFormularioLogin()) return;

    const nombre = dom.login.inputNombre.value.trim();
    const correo = dom.login.inputCorreo.value.trim();

    setLoginLoading(true);

    try {
      // 1.a Crear o recuperar usuario
      const data = await api.crearORecuperarUsuario(nombre, correo);
      state.usuario = data.usuario;

      // 1.b Verificar si ya respondió
      const check = await api.verificarUsuarioRespondio(
        state.usuario.id_usuario,
        CONFIG.ID_FORMULARIO
      );

      if (check.respondio) {
        await cargarRespuestasPrevias();
        return;
      }

      // 1.c Cargar el formulario
      await cargarFormulario();

    } catch (err) {
      mostrarAlerta(dom.login.errorGlobal, err.message);
    } finally {
      setLoginLoading(false);
    }
  }

  /* ── PASO 2: Cargar cuestionario ────────────────────────── */

  async function cargarFormulario() {
    try {
      const data = await api.obtenerFormulario(CONFIG.ID_FORMULARIO);
      state.formulario = data.formulario;
      renderFormulario(state.formulario);
      showView('cuestionario');
    } catch (err) {
      mostrarError(`No se pudo cargar el formulario: ${err.message}`);
    }
  }

  function renderFormulario(formulario) {
    // Encabezado
    dom.cuestionario.tituloFormulario.textContent = formulario.titulo;
    dom.cuestionario.descFormulario.textContent   = formulario.descripcion || '';

    // Preguntas
    dom.cuestionario.preguntasContainer.innerHTML = formulario.preguntas
      .map((p, i) => QuestionComponent.render(p, i))
      .join('');

    // Eventos de escala
    registrarEventosEscala();

    // Progreso inicial
    actualizarProgreso();

    // Evento de cambio para actualizar progreso
    dom.cuestionario.preguntasContainer.addEventListener('change', actualizarProgreso);
    dom.cuestionario.preguntasContainer.addEventListener('input',  actualizarProgreso);
  }

  /* ── Escala interactiva ─────────────────────────────────── */

  function registrarEventosEscala() {
    const scaleBtns = dom.cuestionario.preguntasContainer
      .querySelectorAll('.scale-btn');

    scaleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const idPregunta = btn.dataset.id;
        const grupo      = dom.cuestionario.preguntasContainer
          .querySelectorAll(`.scale-btn[data-id="${idPregunta}"]`);

        // Limpiar selección anterior
        grupo.forEach(b => {
          b.classList.remove('is-selected');
          b.setAttribute('aria-pressed', 'false');
        });

        // Marcar el seleccionado
        btn.classList.add('is-selected');
        btn.setAttribute('aria-pressed', 'true');

        // Actualizar hidden input
        const card        = btn.closest('.pregunta-card');
        const hiddenInput = card.querySelector('input[type="hidden"]');
        if (hiddenInput) {
          hiddenInput.value = btn.dataset.value;
          hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
      });
    });
  }

  /* ── Progreso ────────────────────────────────────────────── */

  function actualizarProgreso() {
    const total     = state.formulario?.preguntas?.length || 0;
    const respondidas = contarPreguntasRespondidas();
    const pct       = total > 0 ? Math.round((respondidas / total) * 100) : 0;

    dom.cuestionario.progressBar.style.width  = `${pct}%`;
    dom.cuestionario.progressLabel.textContent =
      `${respondidas} de ${total} preguntas respondidas`;
  }

  function contarPreguntasRespondidas() {
    const cards = dom.cuestionario.preguntasContainer.querySelectorAll('.pregunta-card');
    let count = 0;

    cards.forEach(card => {
      const tipo = card.dataset.tipo;

      if (tipo === 'texto_corto' || tipo === 'texto_largo') {
        const input = card.querySelector('input, textarea');
        if (input && input.value.trim()) count++;

      } else if (tipo === 'opcion_unica') {
        if (card.querySelector('input[type="radio"]:checked')) count++;

      } else if (tipo === 'opcion_multiple') {
        if (card.querySelector('input[type="checkbox"]:checked')) count++;

      } else if (tipo === 'escala') {
        const hidden = card.querySelector('input[type="hidden"]');
        if (hidden && hidden.value) count++;
      }
    });

    return count;
  }

  /* ── PASO 3: Enviar cuestionario ────────────────────────── */

  async function handleCuestionarioSubmit(e) {
    e.preventDefault();

    if (!validarFormularioCuestionario()) return;

    const respuestas = recolectarRespuestas();

    setCuestionarioLoading(true);

    try {
      await api.guardarRespuestas(
        state.usuario.id_usuario,
        CONFIG.ID_FORMULARIO,
        respuestas
      );
      showView('gracias');

    } catch (err) {
      mostrarAlerta(dom.cuestionario.errorGlobal, err.message);

    } finally {
      setCuestionarioLoading(false);
    }
  }

  /* ── Recolector de respuestas ────────────────────────────── */

  function recolectarRespuestas() {
    const cards = dom.cuestionario.preguntasContainer.querySelectorAll('.pregunta-card');
    const resultado = [];

    cards.forEach(card => {
      const idPregunta = parseInt(card.dataset.id, 10);
      const tipo       = card.dataset.tipo;
      const obj        = { id_pregunta: idPregunta };

      if (tipo === 'texto_corto' || tipo === 'texto_largo') {
        const input = card.querySelector('input, textarea');
        obj.respuesta_texto = input ? input.value.trim() : '';

      } else if (tipo === 'escala') {
        const hidden = card.querySelector('input[type="hidden"]');
        obj.respuesta_numero = hidden && hidden.value ? parseFloat(hidden.value) : null;

      } else if (tipo === 'opcion_unica') {
        const checked = card.querySelector('input[type="radio"]:checked');
        obj.opciones = checked ? [parseInt(checked.value, 10)] : [];

      } else if (tipo === 'opcion_multiple') {
        const checked = card.querySelectorAll('input[type="checkbox"]:checked');
        obj.opciones = Array.from(checked).map(cb => parseInt(cb.value, 10));
      }

      resultado.push(obj);
    });

    return resultado;
  }

  /* ── Respuestas previas ──────────────────────────────────── */

  async function cargarRespuestasPrevias() {
    try {
      const data = await api.obtenerRespuestasUsuario(
        state.usuario.id_usuario,
        CONFIG.ID_FORMULARIO
      );

      dom.yaRespondio.container.innerHTML = data.respuestas
        .map((r, i) => QuestionComponent.renderPreviewer(r, i))
        .join('');

    } catch {
      dom.yaRespondio.container.innerHTML =
        '<p style="color:var(--color-text-muted);">No se pudieron cargar las respuestas.</p>';
    }

    showView('yaRespondio');
  }

  /* ══════════════════════════════════════════════════════════
     VALIDACIÓN
  ══════════════════════════════════════════════════════════ */

  function validarFormularioLogin() {
    let valido = true;

    ocultarAlerta(dom.login.errorGlobal);

    const nombre = dom.login.inputNombre.value.trim();
    const correo = dom.login.inputCorreo.value.trim();

    if (!nombre) {
      mostrarFieldError(dom.login.inputNombre, dom.login.errorNombre, 'El nombre es obligatorio.');
      valido = false;
    } else {
      limpiarFieldError(dom.login.inputNombre, dom.login.errorNombre);
    }

    if (!correo) {
      mostrarFieldError(dom.login.inputCorreo, dom.login.errorCorreo, 'El correo es obligatorio.');
      valido = false;
    } else if (!esCorreoValido(correo)) {
      mostrarFieldError(dom.login.inputCorreo, dom.login.errorCorreo, 'Ingresa un correo electrónico válido.');
      valido = false;
    } else {
      limpiarFieldError(dom.login.inputCorreo, dom.login.errorCorreo);
    }

    return valido;
  }

  function validarFormularioCuestionario() {
    let valido = true;

    ocultarAlerta(dom.cuestionario.errorGlobal);

    const cards = dom.cuestionario.preguntasContainer.querySelectorAll('.pregunta-card');

    cards.forEach(card => {
      const esObligatoria = card.dataset.obligatoria === '1';
      if (!esObligatoria) return;

      const tipo        = card.dataset.tipo;
      let   respondida  = false;

      if (tipo === 'texto_corto' || tipo === 'texto_largo') {
        const input = card.querySelector('input, textarea');
        respondida  = input && input.value.trim().length > 0;

      } else if (tipo === 'opcion_unica') {
        respondida = !!card.querySelector('input[type="radio"]:checked');

      } else if (tipo === 'opcion_multiple') {
        respondida = !!card.querySelector('input[type="checkbox"]:checked');

      } else if (tipo === 'escala') {
        const hidden = card.querySelector('input[type="hidden"]');
        respondida   = hidden && hidden.value !== '';
      }

      if (!respondida) {
        card.classList.add('is-invalid');
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        valido = false;
      } else {
        card.classList.remove('is-invalid');
      }
    });

    if (!valido) {
      mostrarAlerta(
        dom.cuestionario.errorGlobal,
        'Por favor, responde todas las preguntas obligatorias (marcadas con *).'
      );
    }

    return valido;
  }

  /* ══════════════════════════════════════════════════════════
     HELPERS DE UI
  ══════════════════════════════════════════════════════════ */

  function mostrarError(mensaje) {
    dom.error.message.innerHTML = mensaje;
    showView('error');
  }

  function mostrarAlerta(el, mensaje) {
    el.innerHTML = mensaje;
    el.classList.remove('hidden');
  }

  function ocultarAlerta(el) {
    el.textContent = '';
    el.classList.add('hidden');
  }

  function mostrarFieldError(input, errorEl, mensaje) {
    input.classList.add('is-invalid');
    errorEl.textContent = mensaje;
  }

  function limpiarFieldError(input, errorEl) {
    input.classList.remove('is-invalid');
    errorEl.textContent = '';
  }

  function setLoginLoading(cargando) {
    const btn     = dom.login.btnSubmit;
    const text    = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.btn-spinner');

    btn.disabled = cargando;
    text.textContent = cargando ? 'Verificando…' : 'Continuar';
    spinner.classList.toggle('hidden', !cargando);
  }

  function setCuestionarioLoading(cargando) {
    const btn     = dom.cuestionario.btnSubmit;
    const text    = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.btn-spinner');

    btn.disabled = cargando;
    text.textContent = cargando ? 'Enviando…' : 'Enviar respuestas';
    spinner.classList.toggle('hidden', !cargando);
  }

  function esCorreoValido(correo) {
    return /^[\w.-]+@[\w.-]+\.\w+$/.test(correo);
  }

  /* ── Limpiar errores de validación al escribir ──────────── */
  dom.login.inputNombre.addEventListener('input', () => {
    limpiarFieldError(dom.login.inputNombre, dom.login.errorNombre);
  });
  dom.login.inputCorreo.addEventListener('input', () => {
    limpiarFieldError(dom.login.inputCorreo, dom.login.errorCorreo);
  });

  /* ── Arrancar la aplicación ─────────────────────────────── */
  document.addEventListener('DOMContentLoaded', init);
})();
