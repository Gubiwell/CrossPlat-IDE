"""
CAMADA 5 - ROUTES: Rotas de autenticação HTTP
Converte HTTP (JSON) -> Schema -> Service -> HTTP (JSON + status code).
Não contém regra de negócio.
"""
from flask import Blueprint, request, jsonify
from src.schemas.register_user_schema import RegisterUserSchema
from src.schemas.login_schema import LoginSchema
from src.services.register_user_service import RegisterUserService
from src.services.authenticate_user_service import AuthenticateUserService


def create_auth_routes(
    register_user: RegisterUserService,
    authenticate_user: AuthenticateUserService,
) -> Blueprint:
    bp = Blueprint("auth", __name__)

    @bp.post("/register")  # RF01
    def register():
        data = request.get_json() or {}
        try:
            schema = RegisterUserSchema(
                nome=data.get("nome"),
                email=data.get("email"),
                senha=data.get("senha"),
            )
            resultado = register_user.execute(schema)
            return jsonify(resultado.to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @bp.post("/login")  # RF02
    def login():
        data = request.get_json() or {}
        try:
            schema = LoginSchema(
                email=data.get("email"),
                senha=data.get("senha"),
            )
            resultado = authenticate_user.execute(schema)
            return jsonify(resultado.to_dict()), 200
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 401

    return bp
