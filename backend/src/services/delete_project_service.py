"""
CAMADA 4 - SERVICES: DeleteProjectService
Depende APENAS das camadas internas (repositories).
Recebe as implementações concretas por injeção de dependência no construtor (ver app.py).
"""
from src.repositories.i_project_repository import IProjectRepository


class DeleteProjectService:
    """RF04 - Excluir projeto do usuário."""

    def __init__(self, projects: IProjectRepository):
        self.projects = projects

    def execute(self, project_id: int, usuario_id: int) -> None:
        # Só apaga se o projeto pertencer ao usuário
        if not self.projects.delete(project_id, usuario_id):
            raise LookupError("Projeto não encontrado.")
