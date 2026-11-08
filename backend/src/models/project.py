"""
CAMADA 1 - MODELS: Entidade Project
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
    gpl_code: str = ""
    datatype_def: str = ""
    global_functions: str = ""
    deploy_model: str = ""

    def validate(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("O nome do projeto é obrigatório.")
