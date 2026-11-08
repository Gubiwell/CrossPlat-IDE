"""
CAMADA 4 - SERVICES: Interface IPasswordHasher (contrato)
Os services dependem APENAS desta abstração.
A implementação concreta fica na camada externa (infrastructure).
"""
from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool: ...
