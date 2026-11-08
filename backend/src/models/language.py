"""
CAMADA 1 - MODELS: Entidade Language (RF08)
Python puro. Não importa Flask, banco de dados nem nenhuma biblioteca externa.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Language:
    id: Optional[int]
    nome: str
