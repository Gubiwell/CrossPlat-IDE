"""
CAMADA 2 - SCHEMAS: BuildResponseSchema (saída do RF10 - Compilar & Build)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import List
from src.models.generated_file import GeneratedFile


@dataclass
class BuildResponseSchema:
    sucesso: bool
    arquivos: List[GeneratedFile]
    log: str = ""

    def to_dict(self) -> dict:
        return {
            "sucesso": self.sucesso,
            "arquivos": [{"nome": f.nome, "conteudo": f.conteudo} for f in self.arquivos],
            "log": self.log,
        }
