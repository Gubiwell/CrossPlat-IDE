"""
CAMADA 4 - SERVICES: LinkPlatformModelService
Depende APENAS das camadas internas (schemas e repositories).
"""
from src.schemas.link_platform_model_schema import LinkPlatformModelSchema
from src.repositories.i_project_repository import IProjectRepository
from src.repositories.i_platform_model_repository import IPlatformModelRepository


class LinkPlatformModelService:
    """RF07 - Vincular modelo de plataforma do Marketplace a um projeto."""

    def __init__(self, projects: IProjectRepository, platform_models: IPlatformModelRepository):
        self.projects = projects
        self.platform_models = platform_models

    def execute(
        self, project_id: int, usuario_id: int, schema: LinkPlatformModelSchema
    ) -> None:
        if not self.projects.find_by_id(project_id, usuario_id):
            raise LookupError("Projeto não encontrado.")
        if not schema.model_id or not self.platform_models.find_by_id(int(schema.model_id)):
            raise LookupError("Plataforma não encontrada.")

        self.platform_models.link_to_project(project_id, int(schema.model_id))
