"""
CAMADA 5 - ROUTES: Rotas de Linguagens HTTP (RF08)
Converte HTTP -> Service -> HTTP (JSON + status code).
Não contém regra de negócio.
"""
from flask import Blueprint, jsonify
from src.services.list_languages_service import ListLanguagesService


def create_language_routes(
    list_languages: ListLanguagesService,
    auth_required,
) -> Blueprint:
    bp = Blueprint("linguagens", __name__)

    @bp.get("")  # RF08 - listar linguagens disponíveis
    @auth_required
    def list_all():
        resultados = list_languages.execute()
        return jsonify([r.to_dict() for r in resultados]), 200

    return bp
