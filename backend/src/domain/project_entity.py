"""
CAMADA 1 - DOMÍNIO: Entidade Project
Python puro. Não importa Flask, banco de dados nem nenhuma biblioteca externa.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    id: Optional[int]
    nome: str
    usuario_id: int
    data_criacao: Optional[datetime] = None

    def validate(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do projeto é obrigatório.")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
        }

