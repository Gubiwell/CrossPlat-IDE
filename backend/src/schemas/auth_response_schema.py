"""
CAMADA 2 - SCHEMAS: AuthResponseSchema (saída do RF02)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from src.schemas.user_response_schema import UserResponseSchema


@dataclass
class AuthResponseSchema:
    token: str
    user: UserResponseSchema

    def to_dict(self) -> dict:
        return {"token": self.token, "user": self.user.to_dict()}
