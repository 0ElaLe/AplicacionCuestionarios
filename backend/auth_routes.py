"""
auth_routes.py — Rutas de autenticación (registro, login, perfil).
"""
import datetime
from flask import Blueprint, jsonify, request, g
from modelo import registrar_usuario, login_usuario
from middleware import generar_token, requiere_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/registro", methods=["POST"])
def registro():
    data = request.get_json() or {}
    nombre   = (data.get("nombre")   or "").strip()
    correo   = (data.get("correo")   or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not nombre or not correo or not password:
        return jsonify({"error": "nombre, correo y password son obligatorios"}), 400
    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    try:
        usuario = registrar_usuario(nombre, correo, password)
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    payload = {
        "id_usuario": usuario["id_usuario"],
        "nombre":     usuario["nombre"],
        "correo":     usuario["correo"],
        "rol":        usuario["rol"],
        "exp":        datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    token = generar_token(payload)
    return jsonify({"token": token, "usuario": usuario}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    correo   = (data.get("correo")   or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not correo or not password:
        return jsonify({"error": "correo y password son obligatorios"}), 400

    usuario = login_usuario(correo, password)
    if usuario is None:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    payload = {
        "id_usuario": usuario["id_usuario"],
        "nombre":     usuario["nombre"],
        "correo":     usuario["correo"],
        "rol":        usuario["rol"],
        "exp":        datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    token = generar_token(payload)
    return jsonify({"token": token, "usuario": usuario}), 200


@auth_bp.route("/me", methods=["GET"])
@requiere_token
def me():
    return jsonify({"usuario": g.usuario_actual}), 200
