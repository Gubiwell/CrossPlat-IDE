"""
CAMADA 2 - SCHEMAS: CreatePlatformModelSchema (entrada do RF08)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CreatePlatformModelSchema:
    nome: Optional[str]
    codigo: Optional[str] = None
    linguagem: Optional[str] = None
