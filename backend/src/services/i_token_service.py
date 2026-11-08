"""
CAMADA 4 - SERVICES: Interface ITokenService (contrato)
Os services dependem APENAS desta abstração.
A implementação concreta fica na camada externa (infrastructure).
"""
from abc import ABC, abstractmethod
from src.models.user import User


class ITokenService(ABC):
    @abstractmethod
    def generate(self, user: User) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> int:
        """Retorna o id do usuário contido no token (ou lança ValueError)."""
