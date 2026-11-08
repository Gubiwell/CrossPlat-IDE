"""
CAMADA 2 - SCHEMAS: LinkPlatformModelSchema (entrada do RF07)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LinkPlatformModelSchema:
    model_id: Optional[int]
