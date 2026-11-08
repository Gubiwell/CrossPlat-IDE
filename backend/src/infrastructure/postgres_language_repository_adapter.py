"""
CAMADA 6 - INFRASTRUCTURE: Repositório de linguagens PostgreSQL (RF08)
Implementa a interface ILanguageRepository traduzindo para SQL.
"""
from typing import List, Optional
from src.models.language import Language
from src.repositories.i_language_repository import ILanguageRepository
from src.infrastructure.postgres_query_helper import run_query


class PostgresLanguageRepositoryAdapter(ILanguageRepository):
    def list_all(self) -> List[Language]:
        rows = run_query(
            "SELECT id, nome FROM linguagens ORDER BY nome ASC",
            fetch="all",
        )
        return [Language(**row) for row in rows]

    def find_by_name(self, nome: str) -> Optional[Language]:
        row = run_query(
            "SELECT id, nome FROM linguagens WHERE LOWER(nome) = LOWER(%s)",
            (nome,),
        )
        return Language(**row) if row else None
