"""
CAMADA 4 - SERVICES: ListProjectsService
Depende APENAS das camadas internas (schemas e repositories).
Recebe as implementações concretas por injeção de dependência no construtor (ver app.py).
"""
from typing import List
from src.schemas.project_response_schema import ProjectResponseSchema
from src.repositories.i_project_repository import IProjectRepository


class ListProjectsService:
    """RF04 - Listar projetos do usuário."""

    def __init__(self, projects: IProjectRepository):
        self.projects = projects

    def execute(self, usuario_id: int) -> List[ProjectResponseSchema]:
        return [ProjectResponseSchema.from_model(p) for p in self.projects.list_by_user(usuario_id)]
