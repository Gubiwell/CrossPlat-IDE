"""
CAMADA 2 - CASOS DE USO: DeleteProjectService
Depende APENAS do domínio (entidades + portas). Recebe as implementações
concretas por injeção de dependência no construtor (ver app.py).
"""
from src.domain.project_repository_port import ProjectRepositoryPort


class DeleteProjectService:
    """RF04 - Excluir projeto do usuário."""

    def __init__(self, projects: ProjectRepositoryPort):
        self.projects = projects

    def execute(self, project_id: int, usuario_id: int) -> None:
        # Só apaga se o projeto pertencer ao usuário
        if not self.projects.delete(project_id, usuario_id):
            raise LookupError("Projeto não encontrado.")

