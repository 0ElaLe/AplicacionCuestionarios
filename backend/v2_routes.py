"""
v2_routes.py — Rutas v2: formularios dinámicos y avance.
"""
from flask import Blueprint, jsonify, request, g
from middleware import requiere_token
from modelo import (
    crear_formulario_v2,
    obtener_formulario_por_codigo,
    obtener_formulario_por_id,
    obtener_formularios_de_usuario,
    obtener_formularios_publicos,
    obtener_formularios_respondidos,
    guardar_avance,
    obtener_avance,
    editar_formulario_v2,
    archivar_formulario,
    obtener_resultados_formulario,
)

v2_bp = Blueprint("v2", __name__, url_prefix="/api/v2")


# ── Formularios ─────────────────────────────────────────────────

@v2_bp.route("/formularios", methods=["POST"])
@requiere_token
def crear_formulario():
    data = request.get_json() or {}
    titulo       = (data.get("titulo") or "").strip()
    descripcion  = (data.get("descripcion") or "").strip()
    visibilidad  = (data.get("visibilidad") or "publico").strip()
    preguntas    = data.get("preguntas", [])

    if not titulo:
        return jsonify({"error": "El titulo es obligatorio"}), 400
    if not preguntas or not isinstance(preguntas, list):
        return jsonify({"error": "Debes agregar al menos una pregunta"}), 400

    for p in preguntas:
        if not p.get("texto") or not p.get("tipo"):
            return jsonify({"error": "Cada pregunta requiere texto y tipo"}), 400

    try:
        resultado = crear_formulario_v2(
            id_creador=g.usuario_actual["id_usuario"],
            titulo=titulo,
            descripcion=descripcion,
            preguntas_data=preguntas,
            visibilidad=visibilidad,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(resultado), 201


@v2_bp.route("/formularios/<int:id_formulario>", methods=["GET"])
@requiere_token
def get_formulario_por_id(id_formulario):
    formulario = obtener_formulario_por_id(id_formulario, g.usuario_actual["id_usuario"])
    if formulario is None:
        return jsonify({"error": "Formulario no encontrado o sin permiso"}), 404
    return jsonify({"formulario": formulario}), 200


@v2_bp.route("/formularios/<int:id_formulario>", methods=["PUT"])
@requiere_token
def editar_formulario(id_formulario):
    data = request.get_json() or {}
    titulo      = (data.get("titulo") or "").strip()
    descripcion = (data.get("descripcion") or "").strip()
    visibilidad = (data.get("visibilidad") or "publico").strip()
    preguntas   = data.get("preguntas", [])

    if not titulo:
        return jsonify({"error": "El titulo es obligatorio"}), 400

    try:
        resultado = editar_formulario_v2(
            id_formulario=id_formulario,
            id_usuario=g.usuario_actual["id_usuario"],
            titulo=titulo,
            descripcion=descripcion,
            visibilidad=visibilidad,
            preguntas_data=preguntas,
        )
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(resultado), 200


@v2_bp.route("/formularios/<int:id_formulario>/archivar", methods=["PATCH"])
@requiere_token
def toggle_archivar(id_formulario):
    try:
        resultado = archivar_formulario(id_formulario, g.usuario_actual["id_usuario"])
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    return jsonify(resultado), 200


@v2_bp.route("/formularios/<int:id_formulario>/resultados", methods=["GET"])
@requiere_token
def get_resultados(id_formulario):
    datos = obtener_resultados_formulario(id_formulario, g.usuario_actual["id_usuario"])
    if datos is None:
        return jsonify({"error": "Formulario no encontrado o sin permiso"}), 404
    return jsonify(datos), 200


@v2_bp.route("/formularios/codigo/<string:codigo>", methods=["GET"])
def get_formulario_por_codigo(codigo):
    formulario = obtener_formulario_por_codigo(codigo)
    if formulario is None:
        return jsonify({"error": "Formulario no encontrado o no publicado"}), 404
    return jsonify({"formulario": formulario}), 200


@v2_bp.route("/formularios/mios", methods=["GET"])
@requiere_token
def mis_formularios():
    lista = obtener_formularios_de_usuario(g.usuario_actual["id_usuario"])
    return jsonify({"formularios": lista}), 200


@v2_bp.route("/formularios/publicos", methods=["GET"])
def formularios_publicos():
    """Lista todos los cuestionarios publicados con stats básicas."""
    lista = obtener_formularios_publicos()
    return jsonify({"formularios": lista}), 200


@v2_bp.route("/formularios/respondidos/<int:id_usuario>", methods=["GET"])
def formularios_respondidos(id_usuario):
    """Lista los cuestionarios que el usuario ya respondio."""
    lista = obtener_formularios_respondidos(id_usuario)
    return jsonify({"formularios": lista}), 200


# ── Avance ───────────────────────────────────────────────────────

@v2_bp.route("/avance", methods=["POST"])
def guardar_avance_route():
    data          = request.get_json() or {}
    id_usuario    = data.get("id_usuario")
    id_formulario = data.get("id_formulario")
    respuestas    = data.get("respuestas", [])

    if not id_usuario or not id_formulario:
        return jsonify({"error": "id_usuario e id_formulario son obligatorios"}), 400

    guardado = guardar_avance(id_usuario, id_formulario, respuestas)
    if guardado is False:
        return jsonify({"mensaje": "El cuestionario ya fue enviado, no se puede modificar", "ya_enviado": True}), 200

    return jsonify({"mensaje": "Avance guardado", "ya_enviado": False}), 200


@v2_bp.route("/avance/<int:id_usuario>/<int:id_formulario>", methods=["GET"])
def get_avance(id_usuario, id_formulario):
    avance = obtener_avance(id_usuario, id_formulario)
    return jsonify(avance), 200
