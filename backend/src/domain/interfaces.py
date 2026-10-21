"""
CAMADA 1 - DOMÍNIO: Interfaces (contratos)
Os casos de uso dependem APENAS destas abstrações.
As implementações concretas ficam nas camadas externas (adapters / infrastructure).
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import User, Project


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...


class ProjectRepository(ABC):
    @abstractmethod
    def create(self, project: Project) -> Project: ...

    @abstractmethod
    def list_by_user(self, usuario_id: int) -> List[Project]: ...

    @abstractmethod
    def delete(self, project_id: int, usuario_id: int) -> bool: ...


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool: ...


class TokenService(ABC):
    @abstractmethod
    def generate(self, user: User) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> int:
        """Retorna o id do usuário contido no token (ou lança ValueError)."""
