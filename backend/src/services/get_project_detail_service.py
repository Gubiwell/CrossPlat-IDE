"""
CAMADA 4 - SERVICES: GetProjectDetailService
Depende APENAS das camadas internas (schemas e repositories).
"""
from src.schemas.project_detail_response_schema import ProjectDetailResponseSchema
from src.repositories.i_project_repository import IProjectRepository
from src.repositories.i_platform_model_repository import IPlatformModelRepository


class GetProjectDetailService:
    """RF06 - Carregar projeto completo (arquivos e plataformas vinculadas) para o editor."""

    def __init__(self, projects: IProjectRepository, platform_models: IPlatformModelRepository):
        self.projects = projects
        self.platform_models = platform_models

    def execute(self, project_id: int, usuario_id: int) -> ProjectDetailResponseSchema:
        project = self.projects.find_by_id(project_id, usuario_id)
        if not project:
            raise LookupError("Projeto não encontrado.")

        modelos = self.platform_models.list_by_project(project_id)
        return ProjectDetailResponseSchema.from_model(project, modelos)
