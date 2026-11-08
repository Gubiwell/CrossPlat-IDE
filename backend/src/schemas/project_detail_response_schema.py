"""
CAMADA 2 - SCHEMAS: ProjectDetailResponseSchema (saída completa do projeto para a IDE - RF05 a RF09)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from src.models.project import Project
from src.models.platform_model import PlatformModel
from src.schemas.platform_model_response_schema import PlatformModelResponseSchema


@dataclass
class ProjectDetailResponseSchema:
    id: Optional[int]
    nome: str
    usuario_id: int
    data_criacao: Optional[datetime]
    gpl_code: str
    datatype_def: str
    global_functions: str
    deploy_model: str
    modelos_vinculados: List[PlatformModelResponseSchema]

    @classmethod
    def from_model(
        cls, project: Project, modelos: List[PlatformModel]
    ) -> "ProjectDetailResponseSchema":
        return cls(
            id=project.id,
            nome=project.nome,
            usuario_id=project.usuario_id,
            data_criacao=project.data_criacao,
            gpl_code=project.gpl_code or "",
            datatype_def=project.datatype_def or "",
            global_functions=project.global_functions or "",
            deploy_model=project.deploy_model or "",
            modelos_vinculados=[PlatformModelResponseSchema.from_model(m) for m in modelos],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "usuario_id": self.usuario_id,
            "data_criacao": self.data_criacao.isoformat() if self.data_criacao else None,
            "gpl_code": self.gpl_code,
            "datatype_def": self.datatype_def,
            "global_functions": self.global_functions,
            "deploy_model": self.deploy_model,
            "modelos_vinculados": [m.to_dict() for m in self.modelos_vinculados],
        }
