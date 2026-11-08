"""
CAMADA 2 - CASOS DE USO: ListProjectsService
Depende APENAS do domínio (entidades + portas). Recebe as implementações
concretas por injeção de dependência no construtor (ver app.py).
"""
from src.domain.project_repository_port import ProjectRepositoryPort


class ListProjectsService:
    """RF04 - Listar projetos do usuário."""

    def __init__(self, projects: ProjectRepositoryPort):
        self.projects = projects

    def execute(self, usuario_id: int) -> list:
        return [p.to_dict() for p in self.projects.list_by_user(usuario_id)]

