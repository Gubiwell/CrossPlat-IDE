"""
CAMADA 1 - MODELS: Entidade GeneratedFile (RF10)
Python puro. Representa um arquivo de saída produzido pelo gerador Xtext (.jar).
"""
from dataclasses import dataclass


@dataclass
class GeneratedFile:
    nome: str
    conteudo: str
