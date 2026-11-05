"""
Ponto de entrada + COMPOSITION ROOT
É o único lugar que conhece todas as camadas: aqui as implementações
concretas são criadas e injetadas nos casos de uso.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from src.infrastructure.werkzeug_password_hasher_service import WerkzeugPasswordHasherService
from src.infrastructure.jwt_token_service import JwtTokenService
from src.adapters.postgres_user_repository_adapter import PostgresUserRepositoryAdapter
from src.adapters.postgres_project_repository_adapter import PostgresProjectRepositoryAdapter
from src.adapters.auth_middleware import make_auth_required
from src.adapters.auth_controller import create_auth_controller
from src.adapters.project_controller import create_project_controller
from src.use_cases.register_user_service import RegisterUserService
from src.use_cases.authenticate_user_service import AuthenticateUserService
from src.use_cases.create_project_service import CreateProjectService
from src.use_cases.list_projects_service import ListProjectsService
from src.use_cases.delete_project_service import DeleteProjectService


def create_app() -> Flask:
    # Camadas externas (implementações concretas)
    users = PostgresUserRepositoryAdapter()
    projects = PostgresProjectRepositoryAdapter()
    hasher = WerkzeugPasswordHasherService()
    tokens = JwtTokenService(os.environ["JWT_SECRET_KEY"], int(os.getenv("JWT_EXPIRES_HOURS", "24")))

    app = Flask(__name__)
    CORS(app)

    # Injeção de dependências: casos de uso -> controllers
    app.register_blueprint(
        create_auth_controller(
            RegisterUserService(users, hasher),
            AuthenticateUserService(users, hasher, tokens),
        ),
        url_prefix="/api/auth",
    )
    app.register_blueprint(
        create_project_controller(
            CreateProjectService(projects),
            ListProjectsService(projects),
            DeleteProjectService(projects),
            make_auth_required(tokens),
        ),
        url_prefix="/api/projects",
    )

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
