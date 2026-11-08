"""
CAMADA 3 - REPOSITORIES: Interface IProjectRepository (contrato)
Os services dependem APENAS desta abstração.
A implementação concreta fica na camada externa (infrastructure).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.models.project import Project


class IProjectRepository(ABC):
    @abstractmethod
    def create(self, project: Project) -> Project: ...

    @abstractmethod
    def list_by_user(self, usuario_id: int) -> List[Project]: ...

    @abstractmethod
    def find_by_id(self, project_id: int, usuario_id: int) -> Optional[Project]: ...

    @abstractmethod
    def update_files(self, project: Project) -> bool: ...

    @abstractmethod
    def delete(self, project_id: int, usuario_id: int) -> bool: ...
