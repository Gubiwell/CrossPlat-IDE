"""
CAMADA 1 - DOMÍNIO: Porta PasswordHasherPort (contrato)
Os casos de uso dependem APENAS desta abstração.
A implementação concreta fica nas camadas externas (adapters / infrastructure).
"""
from abc import ABC, abstractmethod


class PasswordHasherPort(ABC):
    @abstractmethod
    def hash(self, password: str) -> str: ...

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool: ...

