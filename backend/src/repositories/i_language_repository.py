"""
CAMADA 3 - REPOSITORIES: Interface ILanguageRepository (contrato - RF08)
Os services dependem APENAS desta abstração.
A implementação concreta fica na camada externa (infrastructure).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.language import Language


class ILanguageRepository(ABC):
    @abstractmethod
    def list_all(self) -> List[Language]: ...

    @abstractmethod
    def find_by_name(self, nome: str) -> Optional[Language]: ...
