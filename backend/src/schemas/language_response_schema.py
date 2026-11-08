"""
CAMADA 2 - SCHEMAS: LanguageResponseSchema (saída do RF08)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional
from src.models.language import Language


@dataclass
class LanguageResponseSchema:
    id: Optional[int]
    nome: str

    @classmethod
    def from_model(cls, language: Language) -> "LanguageResponseSchema":
        return cls(id=language.id, nome=language.nome)

    def to_dict(self) -> dict:
        return {"id": self.id, "nome": self.nome}
