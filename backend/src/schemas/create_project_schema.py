"""
CAMADA 2 - SCHEMAS: CreateProjectSchema (entrada do RF03)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateProjectSchema:
    nome: Optional[str]
