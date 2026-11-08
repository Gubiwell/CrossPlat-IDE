"""
CAMADA 2 - SCHEMAS: ProjectResponseSchema (saída do RF03 e RF04)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from src.models.project import Project


@dataclass
class ProjectResponseSchema:
    id: Optional[int]
    nome: str
    data_criacao: Optional[datetime] = None

    @classmethod
    def from_model(cls, project: Project) -> "ProjectResponseSchema":
        return cls(id=project.id, nome=project.nome, data_criacao=project.data_criacao)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
        }
