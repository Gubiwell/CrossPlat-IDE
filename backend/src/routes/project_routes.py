"""
CAMADA 5 - ROUTES: Rotas de projetos e editor HTTP (RF03 a RF10)
Converte HTTP (JSON) -> Schema -> Service -> HTTP (JSON + status code).
Não contém regra de negócio.
"""
from flask import Blueprint, request, jsonify, g
from src.schemas.create_project_schema import CreateProjectSchema
from src.schemas.update_project_schema import UpdateProjectSchema
from src.schemas.link_platform_model_schema import LinkPlatformModelSchema
from src.services.create_project_service import CreateProjectService
from src.services.list_projects_service import ListProjectsService
from src.services.delete_project_service import DeleteProjectService
from src.services.get_project_detail_service import GetProjectDetailService
from src.services.update_project_files_service import UpdateProjectFilesService
from src.services.link_platform_model_service import LinkPlatformModelService
from src.services.unlink_platform_model_service import UnlinkPlatformModelService
from src.services.build_project_service import BuildProjectService


def create_project_routes(
    create_project: CreateProjectService,
    list_projects: ListProjectsService,
    delete_project: DeleteProjectService,
    get_project_detail: GetProjectDetailService,
    update_project_files: UpdateProjectFilesService,
    link_platform_model: LinkPlatformModelService,
    unlink_platform_model: UnlinkPlatformModelService,
    build_project: BuildProjectService,
    auth_required,
) -> Blueprint:
    bp = Blueprint("projects", __name__)

    @bp.post("")  # RF03 - criar projeto
    @auth_required
    def create():
        data = request.get_json() or {}
        try:
            schema = CreateProjectSchema(nome=data.get("nome"))
            resultado = create_project.execute(schema, g.user_id)
            return jsonify(resultado.to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @bp.get("")  # RF04 - listar projetos
    @auth_required
    def list_all():
        resultados = list_projects.execute(g.user_id)
        return jsonify([r.to_dict() for r in resultados]), 200

    @bp.delete("/<int:project_id>")  # RF04 - excluir projeto
    @auth_required
    def delete(project_id):
        try:
            delete_project.execute(project_id, g.user_id)
            return "", 204
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    @bp.get("/<int:project_id>")  # RF06 - carregar projeto para o editor
    @auth_required
    def get_detail(project_id):
        try:
            resultado = get_project_detail.execute(project_id, g.user_id)
            return jsonify(resultado.to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    @bp.put("/<int:project_id>")  # RF05 / RF09 - salvar arquivos do projeto
    @auth_required
    def update_files(project_id):
        data = request.get_json() or {}
        try:
            schema = UpdateProjectSchema(
                gpl_code=data.get("gpl_code"),
                datatype_def=data.get("datatype_def"),
                global_functions=data.get("global_functions"),
                deploy_model=data.get("deploy_model"),
            )
            resultado = update_project_files.execute(project_id, g.user_id, schema)
            return jsonify(resultado.to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @bp.post("/<int:project_id>/link_model")  # RF07 - vincular plataforma ao projeto
    @auth_required
    def link_model(project_id):
        data = request.get_json() or {}
        try:
            schema = LinkPlatformModelSchema(model_id=data.get("model_id"))
            link_platform_model.execute(project_id, g.user_id, schema)
            return jsonify({"sucesso": True}), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @bp.delete("/<int:project_id>/model/<int:model_id>")  # RF07 - desvincular plataforma
    @auth_required
    def unlink_model(project_id, model_id):
        try:
            unlink_platform_model.execute(project_id, model_id, g.user_id)
            return "", 204
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    @bp.post("/<int:project_id>/build")  # RF10 - compilar & build via generator.jar
    @auth_required
    def build(project_id):
        try:
            resultado = build_project.execute(project_id, g.user_id)
            return jsonify(resultado.to_dict()), 200
        except LookupError as e:
            return jsonify({"sucesso": False, "erro": str(e)}), 404
        except RuntimeError as e:
            return jsonify({"sucesso": False, "erro": "Erro no Compilador", "detalhes": str(e)}), 500
        except Exception as e:
            return jsonify({"sucesso": False, "erro": "Erro interno no build", "detalhes": str(e)}), 500

    return bp
