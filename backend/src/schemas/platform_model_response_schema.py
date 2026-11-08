"""
CAMADA 2 - SCHEMAS: PlatformModelResponseSchema (saída do RF07 e RF08)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional
from src.models.platform_model import PlatformModel


@dataclass
class PlatformModelResponseSchema:
    id: Optional[int]
    nome: str
    codigo: str
    criador_id: int
    linguagem_id: Optional[int] = None
    linguagem_nome: Optional[str] = None

    @classmethod
    def from_model(cls, model: PlatformModel) -> "PlatformModelResponseSchema":
        return cls(
            id=model.id,
            nome=model.nome,
            codigo=model.codigo,
            criador_id=model.criador_id,
            linguagem_id=model.linguagem_id,
            linguagem_nome=model.linguagem_nome,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "codigo": self.codigo,
            "criador_id": self.criador_id,
            "linguagem_id": self.linguagem_id,
            "linguagem": self.linguagem_nome,
        }
