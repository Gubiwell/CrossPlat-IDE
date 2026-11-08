"""
CAMADA 4 - SERVICES: CreateProjectService
Depende APENAS das camadas internas (models, schemas e repositories).
Recebe as implementações concretas por injeção de dependência no construtor (ver app.py).
"""
from src.models.project import Project
from src.schemas.create_project_schema import CreateProjectSchema
from src.schemas.project_response_schema import ProjectResponseSchema
from src.repositories.i_project_repository import IProjectRepository


class CreateProjectService:
    """RF03 - Criar projeto (por enquanto, apenas nome)."""

    def __init__(self, projects: IProjectRepository):
        self.projects = projects

    def execute(self, schema: CreateProjectSchema, usuario_id: int) -> ProjectResponseSchema:
        project = Project(id=None, nome=(schema.nome or "").strip(), usuario_id=usuario_id)
        project.validate()
        return ProjectResponseSchema.from_model(self.projects.create(project))
