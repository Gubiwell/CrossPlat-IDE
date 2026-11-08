"""
CAMADA 4 - SERVICES: UpdateProjectFilesService
Depende APENAS das camadas internas (schemas e repositories).
"""
from src.schemas.update_project_schema import UpdateProjectSchema
from src.schemas.project_detail_response_schema import ProjectDetailResponseSchema
from src.repositories.i_project_repository import IProjectRepository
from src.repositories.i_platform_model_repository import IPlatformModelRepository


class UpdateProjectFilesService:
    """RF05 / RF09 - Salvar código dos arquivos pertencentes ao projeto."""

    def __init__(self, projects: IProjectRepository, platform_models: IPlatformModelRepository):
        self.projects = projects
        self.platform_models = platform_models

    def execute(
        self, project_id: int, usuario_id: int, schema: UpdateProjectSchema
    ) -> ProjectDetailResponseSchema:
        project = self.projects.find_by_id(project_id, usuario_id)
        if not project:
            raise LookupError("Projeto não encontrado.")

        if schema.gpl_code is not None:
            project.gpl_code = schema.gpl_code
        if schema.datatype_def is not None:
            project.datatype_def = schema.datatype_def
        if schema.global_functions is not None:
            project.global_functions = schema.global_functions
        if schema.deploy_model is not None:
            project.deploy_model = schema.deploy_model

        self.projects.update_files(project)
        modelos = self.platform_models.list_by_project(project_id)
        return ProjectDetailResponseSchema.from_model(project, modelos)
