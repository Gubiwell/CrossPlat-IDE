"""
CAMADA 3 - ADAPTERS (entrada): Middleware de autenticação JWT
Lê o cabeçalho "Authorization: Bearer <token>" e coloca o id do usuário em g.user_id.
"""
from functools import wraps
from flask import request, jsonify, g
from src.domain.interfaces import TokenService


def make_auth_required(tokens: TokenService):
    def auth_required(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            header = request.headers.get("Authorization", "")
            if not header.startswith("Bearer "):
                return jsonify({"erro": "Token não informado."}), 401
            try:
                g.user_id = tokens.decode(header[len("Bearer "):])
            except ValueError as e:
                return jsonify({"erro": str(e)}), 401
            return view(*args, **kwargs)
        return wrapper
    return auth_required
