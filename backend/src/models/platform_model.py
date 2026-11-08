"""
CAMADA 1 - MODELS: Entidade PlatformModel (RF07, RF08)
Python puro. Representa um modelo de plataforma do Marketplace com template protegido.
"""
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PlatformModel:
    id: Optional[int]
    nome: str
    codigo: str
    criador_id: int
    linguagem_id: Optional[int] = None
    linguagem_nome: Optional[str] = None
    data_criacao: Optional[datetime] = None

    def validate(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Informe o nome da plataforma.")
        if not self.codigo or not self.codigo.strip():
            raise ValueError("O código do template da plataforma é obrigatório.")
        if not re.match(r"^platform\s+\S+\s*:\s*\S+\s*\{[\s\S]*\}\s*$", self.codigo.strip()):
            raise ValueError(
                "O template da plataforma deve manter a estrutura protegida: platform <nome>: <linguagem> { ... }"
            )
