"""
CAMADA 2 - SCHEMAS: UserResponseSchema (saída sem senha)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional
from src.models.user import User


@dataclass
class UserResponseSchema:
    id: Optional[int]
    nome: str
    email: str

    @classmethod
    def from_model(cls, user: User) -> "UserResponseSchema":
        # A senha nunca é exposta
        return cls(id=user.id, nome=user.nome, email=user.email)

    def to_dict(self) -> dict:
        return {"id": self.id, "nome": self.nome, "email": self.email}
