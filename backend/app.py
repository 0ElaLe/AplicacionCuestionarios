from flask import Flask
from flask_cors import CORS

from rutas import api
from modelo import inicializar_bd


def create_app():
    app = Flask(__name__)

    # Permite que Angular consuma la API desde otro puerto
    CORS(app)

    # Registra las rutas bajo /api
    app.register_blueprint(api)

    # Crea tablas e inserta datos iniciales
    inicializar_bd()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5000)