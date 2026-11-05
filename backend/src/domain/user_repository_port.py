"""
CAMADA 1 - DOMÍNIO: Porta UserRepositoryPort (contrato)
Os casos de uso dependem APENAS desta abstração.
A implementação concreta fica nas camadas externas (adapters / infrastructure).
"""
from abc import ABC, abstractmethod
from typing import Optional
from src.domain.user_entity import User


class UserRepositoryPort(ABC):
    @abstractmethod
    def create(self, user: User) -> User: ...

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]: ...

