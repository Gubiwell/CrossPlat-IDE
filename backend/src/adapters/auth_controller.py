"""
CAMADA 3 - ADAPTERS (entrada): Controller de autenticação HTTP
Converte HTTP (JSON) -> chamada do caso de uso -> HTTP (JSON + status code).
Não contém regra de negócio.
"""
from flask import Blueprint, request, jsonify


def create_auth_controller(register_user, authenticate_user) -> Blueprint:
    bp = Blueprint("auth", __name__)

    @bp.post("/register")  # RF01
    def register():
        data = request.get_json() or {}
        try:
            user = register_user.execute(data.get("nome"), data.get("email"), data.get("senha"))
            return jsonify(user), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @bp.post("/login")  # RF02
    def login():
        data = request.get_json() or {}
        try:
            return jsonify(authenticate_user.execute(data.get("email"), data.get("senha"))), 200
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 401

    return bp

