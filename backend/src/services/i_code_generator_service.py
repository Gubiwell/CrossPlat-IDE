"""
CAMADA 4 - SERVICES: Interface ICodeGeneratorService (contrato - RF10)
Os services dependem APENAS desta abstração.
A implementação concreta (execução do JAR) fica na camada externa (infrastructure).
"""
from abc import ABC, abstractmethod
from typing import List, Tuple
from src.models.project import Project
from src.models.platform_model import PlatformModel
from src.models.generated_file import GeneratedFile


class ICodeGeneratorService(ABC):
    @abstractmethod
    def generate(
        self, project: Project, modelos: List[PlatformModel]
    ) -> Tuple[List[GeneratedFile], str]:
        """Executa o gerador e retorna (lista de arquivos gerados, log do processo)."""
