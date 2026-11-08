"""
CAMADA 2 - CASOS DE USO: CreateProjectService
Depende APENAS do domínio (entidades + portas). Recebe as implementações
concretas por injeção de dependência no construtor (ver app.py).
"""
from src.domain.project_entity import Project
from src.domain.project_repository_port import ProjectRepositoryPort


class CreateProjectService:
    """RF03 - Criar projeto (por enquanto, apenas nome)."""

    def __init__(self, projects: ProjectRepositoryPort):
        self.projects = projects

    def execute(self, nome: str, usuario_id: int) -> dict:
        project = Project(id=None, nome=(nome or "").strip(), usuario_id=usuario_id)
        project.validate()
        return self.projects.create(project).to_dict()

