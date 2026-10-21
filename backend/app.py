"""
Ponto de entrada + COMPOSITION ROOT
É o único lugar que conhece todas as camadas: aqui as implementações
concretas são criadas e injetadas nos casos de uso.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from src.infrastructure.security import WerkzeugPasswordHasher, JwtTokenService
from src.adapters.repositories import PostgresUserRepository, PostgresProjectRepository
from src.adapters.middleware import make_auth_required
from src.adapters.controllers import create_auth_controller, create_project_controller
from src.use_cases.use_cases import (
    RegisterUserUseCase,
    AuthenticateUserUseCase,
    CreateProjectUseCase,
    ListProjectsUseCase,
    DeleteProjectUseCase,
)


def create_app() -> Flask:
    # Camadas externas (implementações concretas)
    users = PostgresUserRepository()
    projects = PostgresProjectRepository()
    hasher = WerkzeugPasswordHasher()
    tokens = JwtTokenService(os.environ["JWT_SECRET_KEY"], int(os.getenv("JWT_EXPIRES_HOURS", "24")))

    app = Flask(__name__)
    CORS(app)

    # Injeção de dependências: casos de uso -> controllers
    app.register_blueprint(
        create_auth_controller(
            RegisterUserUseCase(users, hasher),
            AuthenticateUserUseCase(users, hasher, tokens),
        ),
        url_prefix="/api/auth",
    )
    app.register_blueprint(
        create_project_controller(
            CreateProjectUseCase(projects),
            ListProjectsUseCase(projects),
            DeleteProjectUseCase(projects),
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
