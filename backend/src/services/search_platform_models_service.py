"""
CAMADA 4 - SERVICES: SearchPlatformModelsService
Depende APENAS das camadas internas (schemas e repositories).
"""
from typing import List
from src.schemas.platform_model_response_schema import PlatformModelResponseSchema
from src.repositories.i_platform_model_repository import IPlatformModelRepository


class SearchPlatformModelsService:
    """RF07 - Buscar modelos de plataforma no Marketplace global."""

    def __init__(self, platform_models: IPlatformModelRepository):
        self.platform_models = platform_models

    def execute(self, query: str) -> List[PlatformModelResponseSchema]:
        modelos = self.platform_models.search((query or "").strip())
        return [PlatformModelResponseSchema.from_model(m) for m in modelos]
