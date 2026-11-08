"""
CAMADA 2 - SCHEMAS: UpdatePlatformModelSchema (entrada do RF05 / RF08)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdatePlatformModelSchema:
    codigo: Optional[str]
