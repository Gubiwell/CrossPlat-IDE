"""
CAMADA 1 - DOMÍNIO: Entidades
Python puro. Não importa Flask, banco de dados nem nenhuma biblioteca externa.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    id: Optional[int]
    nome: str
    email: str
    senha: str
    data_criacao: Optional[datetime] = None

    def validate(self) -> None:
        if not self.nome or len(self.nome.strip()) < 2:
            raise ValueError("O nome deve ter pelo menos 2 caracteres.")
        if not self.email or "@" not in self.email:
            raise ValueError("E-mail inválido.")
        if not self.senha or len(self.senha) < 6:
            raise ValueError("A senha deve ter pelo menos 6 caracteres.")

    def to_dict(self) -> dict:
        # A senha nunca é exposta
        return {"id": self.id, "nome": self.nome, "email": self.email}


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
