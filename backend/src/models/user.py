"""
CAMADA 1 - MODELS: Entidade User
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
