"""
middleware.py — Decorador JWT para proteger rutas.
"""
import os
import jwt
from functools import wraps
from flask import request, jsonify, g

JWT_SECRET = os.environ.get("JWT_SECRET", "clave-secreta-iimas-2026")
JWT_ALGORITHM = "HS256"


def generar_token(payload: dict) -> str:
    """Genera un JWT firmado con los datos del usuario."""
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    """Decodifica y valida un JWT. Lanza excepción si es inválido."""
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def requiere_token(f):
    """
    Decorador que valida el Bearer token del header Authorization.
    Inyecta g.usuario_actual con los datos del token.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Token de autorizacion requerido"}), 401

        token = auth_header[7:]
        try:
            payload = decodificar_token(token)
            g.usuario_actual = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token ha expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token invalido"}), 401

        return f(*args, **kwargs)
    return decorated
