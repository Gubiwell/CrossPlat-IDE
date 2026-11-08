"""
CAMADA 4 - SERVICES: BuildProjectService
Depende APENAS das camadas internas (schemas, repositories e interfaces de services).
"""
from src.schemas.build_response_schema import BuildResponseSchema
from src.repositories.i_project_repository import IProjectRepository
from src.repositories.i_platform_model_repository import IPlatformModelRepository
from src.services.i_code_generator_service import ICodeGeneratorService


class BuildProjectService:
    """RF10 - Geração de código (Build) via gerador Xtext (.jar)."""

    def __init__(
        self,
        projects: IProjectRepository,
        platform_models: IPlatformModelRepository,
        generator: ICodeGeneratorService,
    ):
        self.projects = projects
        self.platform_models = platform_models
        self.generator = generator

    def execute(self, project_id: int, usuario_id: int) -> BuildResponseSchema:
        project = self.projects.find_by_id(project_id, usuario_id)
        if not project:
            raise LookupError("Projeto não encontrado.")

        modelos = self.platform_models.list_by_project(project_id)
        arquivos, log = self.generator.generate(project, modelos)
        return BuildResponseSchema(sucesso=True, arquivos=arquivos, log=log)
