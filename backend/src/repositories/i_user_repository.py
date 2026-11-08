"""
CAMADA 3 - REPOSITORIES: Interface IUserRepository (contrato)
Os services dependem APENAS desta abstração.
A implementação concreta fica na camada externa (infrastructure).
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.models.user import User


class IUserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...
