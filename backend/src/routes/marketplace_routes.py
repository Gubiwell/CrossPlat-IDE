"""
CAMADA 5 - ROUTES: Rotas do Marketplace de Plataformas HTTP (RF05, RF07, RF08)
Converte HTTP (JSON) -> Schema -> Service -> HTTP (JSON + status code).
Não contém regra de negócio.
"""
from flask import Blueprint, request, jsonify, g
from src.schemas.create_platform_model_schema import CreatePlatformModelSchema
from src.schemas.update_platform_model_schema import UpdatePlatformModelSchema
from src.services.search_platform_models_service import SearchPlatformModelsService
from src.services.create_platform_model_service import CreatePlatformModelService
from src.services.update_platform_model_service import UpdatePlatformModelService


def create_marketplace_routes(
    search_models: SearchPlatformModelsService,
    create_model: CreatePlatformModelService,
    update_model: UpdatePlatformModelService,
    auth_required,
) -> Blueprint:
    bp = Blueprint("marketplace", __name__)

    @bp.get("")  # RF07 - buscar plataformas no marketplace
    @auth_required
    def search():
        query = request.args.get("q", "")
        resultados = search_models.execute(query)
        return jsonify([r.to_dict() for r in resultados]), 200

    @bp.post("")  # RF08 - criar nova plataforma
    @auth_required
    def create():
        data = request.get_json() or {}
        try:
            schema = CreatePlatformModelSchema(
                nome=data.get("nome"),
                codigo=data.get("codigo"),
                linguagem=data.get("linguagem"),
            )
            resultado = create_model.execute(schema, g.user_id)
            return jsonify(resultado.to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @bp.put("/<int:model_id>")  # RF05 / RF08 - salvar código de plataforma
    @auth_required
    def update(model_id):
        data = request.get_json() or {}
        try:
            schema = UpdatePlatformModelSchema(codigo=data.get("codigo"))
            resultado = update_model.execute(model_id, g.user_id, schema)
            return jsonify(resultado.to_dict()), 200
        except PermissionError as e:
            return jsonify({"erro": str(e)}), 403
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    return bp
