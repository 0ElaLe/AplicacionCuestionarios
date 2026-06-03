import re

from modelo import (
    crear_o_obtener_usuario,
    obtener_formulario,
    usuario_respondio_formulario,
    guardar_respuestas,
    obtener_respuestas_usuario,
    eliminar_intento_usuario
)


def correo_valido(correo):
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, correo) is not None


def crear_o_recuperar_usuario_controller(data):
    if not data:
        return {
            "error": "No se recibió información del usuario"
        }, 400

    nombre = data.get("nombre")
    correo = data.get("correo")

    if not nombre or not correo:
        return {
            "error": "El nombre y el correo son obligatorios"
        }, 400

    if not correo_valido(correo):
        return {
            "error": "El correo no tiene un formato válido"
        }, 400

    usuario = crear_o_obtener_usuario(nombre, correo)

    return {
        "mensaje": "Usuario identificado correctamente",
        "usuario": usuario
    }, 200


def obtener_formulario_controller(id_formulario):
    formulario = obtener_formulario(id_formulario)

    if formulario is None:
        return {
            "error": "El formulario no existe"
        }, 404

    return {
        "formulario": formulario
    }, 200


def verificar_usuario_respondio_controller(id_usuario, id_formulario):
    respondio = usuario_respondio_formulario(id_usuario, id_formulario)

    return {
        "id_usuario": id_usuario,
        "id_formulario": id_formulario,
        "respondio": respondio
    }, 200


def guardar_respuestas_controller(data):
    if not data:
        return {
            "error": "No se recibió información para guardar respuestas"
        }, 400

    id_usuario = data.get("id_usuario")
    id_formulario = data.get("id_formulario")
    respuestas = data.get("respuestas")

    if not id_usuario or not id_formulario:
        return {
            "error": "Faltan id_usuario o id_formulario"
        }, 400

    if not isinstance(respuestas, list) or len(respuestas) == 0:
        return {
            "error": "Debe enviarse una lista de respuestas"
        }, 400

    if usuario_respondio_formulario(id_usuario, id_formulario):
        return {
            "error": "Este usuario ya respondió el formulario"
        }, 409

    try:
        resultado = guardar_respuestas(
            id_usuario=id_usuario,
            id_formulario=id_formulario,
            respuestas=respuestas
        )

        return {
            "mensaje": "Respuestas guardadas correctamente",
            "id_intento": resultado["id_intento"]
        }, 201

    except ValueError as error:
        return {
            "error": str(error)
        }, 400

    except Exception as error:
        return {
            "error": "Ocurrió un error inesperado al guardar las respuestas",
            "detalle": str(error)
        }, 500


def obtener_respuestas_usuario_controller(id_usuario, id_formulario):
    respuestas = obtener_respuestas_usuario(id_usuario, id_formulario)

    if respuestas is None:
        return {
            "error": "El usuario no ha respondido este formulario"
        }, 404

    return {
        "id_usuario": id_usuario,
        "id_formulario": id_formulario,
        "respuestas": respuestas
    }, 200


def reiniciar_formulario_controller(id_usuario, id_formulario):
    try:
        eliminado = eliminar_intento_usuario(id_usuario, id_formulario)

        if not eliminado:
            return {
                "error": "No se encontró un intento previo para este usuario y formulario"
            }, 404

        return {
            "mensaje": "Intento eliminado correctamente. El usuario puede volver a responder.",
            "id_usuario": id_usuario,
            "id_formulario": id_formulario
        }, 200

    except Exception as error:
        return {
            "error": "Ocurrió un error al reiniciar el formulario",
            "detalle": str(error)
        }, 500