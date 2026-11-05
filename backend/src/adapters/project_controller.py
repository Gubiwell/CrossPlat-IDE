"""
CAMADA 3 - ADAPTERS (entrada): Controller de projetos HTTP
Converte HTTP (JSON) -> chamada do caso de uso -> HTTP (JSON + status code).
Não contém regra de negócio.
"""
from flask import Blueprint, request, jsonify, g


def create_project_controller(create_project, list_projects, delete_project, auth_required) -> Blueprint:
    bp = Blueprint("projects", __name__)

    @bp.post("")  # RF03
    @auth_required
    def create():
        data = request.get_json() or {}
        try:
            return jsonify(create_project.execute(data.get("nome"), g.user_id)), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @bp.get("")  # RF04 - listar
    @auth_required
    def list_all():
        return jsonify(list_projects.execute(g.user_id)), 200

    @bp.delete("/<int:project_id>")  # RF04 - excluir
    @auth_required
    def delete(project_id):
        try:
            delete_project.execute(project_id, g.user_id)
            return "", 204
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    return bp

