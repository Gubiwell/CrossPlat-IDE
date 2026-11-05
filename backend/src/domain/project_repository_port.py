"""
CAMADA 1 - DOMÍNIO: Porta ProjectRepositoryPort (contrato)
Os casos de uso dependem APENAS desta abstração.
A implementação concreta fica nas camadas externas (adapters / infrastructure).
"""
from abc import ABC, abstractmethod
from typing import List
from src.domain.project_entity import Project


class ProjectRepositoryPort(ABC):
    @abstractmethod
    def create(self, project: Project) -> Project: ...

    @abstractmethod
    def list_by_user(self, usuario_id: int) -> List[Project]: ...

    @abstractmethod
    def delete(self, project_id: int, usuario_id: int) -> bool: ...

