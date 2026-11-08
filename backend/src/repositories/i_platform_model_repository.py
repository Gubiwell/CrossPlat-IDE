"""
CAMADA 3 - REPOSITORIES: Interface IPlatformModelRepository (contrato - RF07 e RF08)
Os services dependem APENAS desta abstração.
A implementação concreta fica na camada externa (infrastructure).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.platform_model import PlatformModel


class IPlatformModelRepository(ABC):
    @abstractmethod
    def create(self, model: PlatformModel) -> PlatformModel: ...

    @abstractmethod
    def find_by_id(self, model_id: int) -> Optional[PlatformModel]: ...

    @abstractmethod
    def find_by_name(self, nome: str) -> Optional[PlatformModel]: ...

    @abstractmethod
    def search(self, query: str) -> List[PlatformModel]: ...

    @abstractmethod
    def update_code(self, model_id: int, codigo: str) -> bool: ...

    @abstractmethod
    def list_by_project(self, project_id: int) -> List[PlatformModel]: ...

    @abstractmethod
    def link_to_project(self, project_id: int, model_id: int) -> None: ...

    @abstractmethod
    def unlink_from_project(self, project_id: int, model_id: int) -> bool: ...
