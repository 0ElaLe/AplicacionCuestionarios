from flask import Blueprint, jsonify, request

from controllers import (
    crear_o_recuperar_usuario_controller,
    obtener_formulario_controller,
    verificar_usuario_respondio_controller,
    guardar_respuestas_controller,
    obtener_respuestas_usuario_controller,
    reiniciar_formulario_controller
)

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "mensaje": "Backend Flask funcionando correctamente"
    }), 200


@api.route("/usuarios", methods=["POST"])
def crear_o_recuperar_usuario():
    data = request.get_json()

    respuesta, status = crear_o_recuperar_usuario_controller(data)

    return jsonify(respuesta), status


@api.route("/formularios/<int:id_formulario>", methods=["GET"])
def obtener_formulario(id_formulario):
    respuesta, status = obtener_formulario_controller(id_formulario)

    return jsonify(respuesta), status


@api.route(
    "/usuarios/<int:id_usuario>/respondio/<int:id_formulario>",
    methods=["GET"]
)
def verificar_usuario_respondio(id_usuario, id_formulario):
    respuesta, status = verificar_usuario_respondio_controller(
        id_usuario,
        id_formulario
    )

    return jsonify(respuesta), status


@api.route("/respuestas", methods=["POST"])
def guardar_respuestas():
    data = request.get_json()

    respuesta, status = guardar_respuestas_controller(data)

    return jsonify(respuesta), status


@api.route(
    "/usuarios/<int:id_usuario>/respuestas/<int:id_formulario>",
    methods=["GET"]
)
def obtener_respuestas_usuario(id_usuario, id_formulario):
    respuesta, status = obtener_respuestas_usuario_controller(
        id_usuario,
        id_formulario
    )

    return jsonify(respuesta), status


@api.route(
    "/usuarios/<int:id_usuario>/respuestas/<int:id_formulario>",
    methods=["DELETE"]
)
def reiniciar_formulario(id_usuario, id_formulario):
    respuesta, status = reiniciar_formulario_controller(
        id_usuario,
        id_formulario
    )

    return jsonify(respuesta), status