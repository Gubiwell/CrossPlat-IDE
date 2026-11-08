"""
CAMADA 2 - SCHEMAS: UpdateProjectSchema (entrada do RF05 / RF09)
Dataclass em Python puro, sem bibliotecas externas.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateProjectSchema:
    gpl_code: Optional[str] = None
    datatype_def: Optional[str] = None
    global_functions: Optional[str] = None
    deploy_model: Optional[str] = None
