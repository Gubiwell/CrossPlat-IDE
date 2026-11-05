"""
CAMADA 1 - DOMÍNIO: Porta TokenServicePort (contrato)
Os casos de uso dependem APENAS desta abstração.
A implementação concreta fica nas camadas externas (adapters / infrastructure).
"""
from abc import ABC, abstractmethod
from src.domain.user_entity import User


class TokenServicePort(ABC):
    @abstractmethod
    def generate(self, user: User) -> str: ...

    @abstractmethod
    def decode(self, token: str) -> int:
        """Retorna o id do usuário contido no token (ou lança ValueError)."""

