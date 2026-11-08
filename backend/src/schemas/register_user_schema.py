"""
CAMADA 2 - SCHEMAS: RegisterUserSchema (entrada do RF01)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RegisterUserSchema:
    nome: Optional[str]
    email: Optional[str]
    senha: Optional[str]
