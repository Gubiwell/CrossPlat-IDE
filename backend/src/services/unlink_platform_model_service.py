"""
CAMADA 4 - SERVICES: UnlinkPlatformModelService
Depende APENAS das camadas internas (repositories).
"""
from src.repositories.i_project_repository import IProjectRepository
from src.repositories.i_platform_model_repository import IPlatformModelRepository


class UnlinkPlatformModelService:
    """RF07 - Desvincular modelo de plataforma de um projeto."""

    def __init__(self, projects: IProjectRepository, platform_models: IPlatformModelRepository):
        self.projects = projects
        self.platform_models = platform_models

    def execute(self, project_id: int, model_id: int, usuario_id: int) -> None:
        if not self.projects.find_by_id(project_id, usuario_id):
            raise LookupError("Projeto não encontrado.")
        if not self.platform_models.unlink_from_project(project_id, model_id):
            raise LookupError("Plataforma não vinculada ao projeto.")
