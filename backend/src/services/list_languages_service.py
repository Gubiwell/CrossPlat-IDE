"""
CAMADA 4 - SERVICES: ListLanguagesService
Depende APENAS das camadas internas (schemas e repositories).
"""
from typing import List
from src.schemas.language_response_schema import LanguageResponseSchema
from src.repositories.i_language_repository import ILanguageRepository


class ListLanguagesService:
    """RF08 - Listar linguagens base disponíveis para criação de plataformas."""

    def __init__(self, languages: ILanguageRepository):
        self.languages = languages

    def execute(self) -> List[LanguageResponseSchema]:
        return [LanguageResponseSchema.from_model(lang) for lang in self.languages.list_all()]
