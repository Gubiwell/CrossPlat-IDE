"""
Ponto de entrada + COMPOSITION ROOT
É o único lugar que conhece todas as camadas: aqui as implementações
concretas são criadas e injetadas nos services.
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS

from src.infrastructure.postgres_connection import ensure_schema
from src.infrastructure.werkzeug_password_hasher_service import WerkzeugPasswordHasherService
from src.infrastructure.jwt_token_service import JwtTokenService
from src.infrastructure.postgres_user_repository_adapter import PostgresUserRepositoryAdapter
from src.infrastructure.postgres_project_repository_adapter import PostgresProjectRepositoryAdapter
from src.infrastructure.postgres_platform_model_repository_adapter import PostgresPlatformModelRepositoryAdapter
from src.infrastructure.postgres_language_repository_adapter import PostgresLanguageRepositoryAdapter
from src.infrastructure.java_code_generator_service import JavaCodeGeneratorService

from src.routes.auth_middleware import make_auth_required
from src.routes.auth_routes import create_auth_routes
from src.routes.project_routes import create_project_routes
from src.routes.marketplace_routes import create_marketplace_routes
from src.routes.language_routes import create_language_routes

from src.services.register_user_service import RegisterUserService
from src.services.authenticate_user_service import AuthenticateUserService
from src.services.create_project_service import CreateProjectService
from src.services.list_projects_service import ListProjectsService
from src.services.delete_project_service import DeleteProjectService
from src.services.get_project_detail_service import GetProjectDetailService
from src.services.update_project_files_service import UpdateProjectFilesService
from src.services.link_platform_model_service import LinkPlatformModelService
from src.services.unlink_platform_model_service import UnlinkPlatformModelService
from src.services.build_project_service import BuildProjectService
from src.services.search_platform_models_service import SearchPlatformModelsService
from src.services.create_platform_model_service import CreatePlatformModelService
from src.services.update_platform_model_service import UpdatePlatformModelService
from src.services.list_languages_service import ListLanguagesService


def create_app() -> Flask:
    # Garante que as colunas e tabelas de RF05 a RF10 existam mesmo em volumes antigos
    try:
        ensure_schema()
    except Exception:
        pass

    # Camada 6 - Infrastructure (implementações concretas)
    users = PostgresUserRepositoryAdapter()
    projects = PostgresProjectRepositoryAdapter()
    platforms = PostgresPlatformModelRepositoryAdapter()
    languages = PostgresLanguageRepositoryAdapter()
    hasher = WerkzeugPasswordHasherService()
    tokens = JwtTokenService(os.environ["JWT_SECRET_KEY"], int(os.getenv("JWT_EXPIRES_HOURS", "24")))
    generator = JavaCodeGeneratorService(
        jar_path=os.getenv("JAR_PATH", "/generator/generator.jar"),
        temp_build_dir=os.getenv("TEMP_BUILD_DIR", "/tmp/crossplat_builds"),
    )

    auth_required = make_auth_required(tokens)

    app = Flask(__name__)
    CORS(app)

    # Injeção de dependências: services -> routes
    app.register_blueprint(
        create_auth_routes(
            RegisterUserService(users, hasher),
            AuthenticateUserService(users, hasher, tokens),
        ),
        url_prefix="/api/auth",
    )
    app.register_blueprint(
        create_project_routes(
            CreateProjectService(projects),
            ListProjectsService(projects),
            DeleteProjectService(projects),
            GetProjectDetailService(projects, platforms),
            UpdateProjectFilesService(projects, platforms),
            LinkPlatformModelService(projects, platforms),
            UnlinkPlatformModelService(projects, platforms),
            BuildProjectService(projects, platforms, generator),
            auth_required,
        ),
        url_prefix="/api/projects",
    )
    app.register_blueprint(
        create_marketplace_routes(
            SearchPlatformModelsService(platforms),
            CreatePlatformModelService(platforms, languages),
            UpdatePlatformModelService(platforms),
            auth_required,
        ),
        url_prefix="/api/marketplace",
    )
    app.register_blueprint(
        create_language_routes(
            ListLanguagesService(languages),
            auth_required,
        ),
        url_prefix="/api/linguagens",
    )

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=True)
