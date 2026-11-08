"""
CAMADA 2 - SCHEMAS: LoginSchema (entrada do RF02)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LoginSchema:
    email: Optional[str]
    senha: Optional[str]
