"""
CAMADA 6 - INFRASTRUCTURE: Repositório de modelos de plataforma PostgreSQL (RF07, RF08)
Implementa a interface IPlatformModelRepository traduzindo para SQL.
"""
from typing import List, Optional
from src.models.platform_model import PlatformModel
from src.repositories.i_platform_model_repository import IPlatformModelRepository
from src.infrastructure.postgres_query_helper import run_query

SELECT_MODEL_SQL = """
    SELECT m.id, m.nome, m.codigo, m.criador_id, m.linguagem_id,
           l.nome AS linguagem_nome, m.data_criacao
    FROM modelosPlataforma m
    LEFT JOIN linguagens l ON l.id = m.linguagem_id
"""


class PostgresPlatformModelRepositoryAdapter(IPlatformModelRepository):
    def create(self, model: PlatformModel) -> PlatformModel:
        row = run_query(
            "INSERT INTO modelosPlataforma (nome, codigo, criador_id, linguagem_id) "
            "VALUES (%s, %s, %s, %s) RETURNING id, data_criacao",
            (model.nome, model.codigo, model.criador_id, model.linguagem_id),
        )
        model.id = row["id"]
        model.data_criacao = row["data_criacao"]
        return model

    def find_by_id(self, model_id: int) -> Optional[PlatformModel]:
        row = run_query(f"{SELECT_MODEL_SQL} WHERE m.id = %s", (model_id,))
        return PlatformModel(**row) if row else None

    def find_by_name(self, nome: str) -> Optional[PlatformModel]:
        row = run_query(f"{SELECT_MODEL_SQL} WHERE LOWER(m.nome) = LOWER(%s)", (nome,))
        return PlatformModel(**row) if row else None

    def search(self, query: str) -> List[PlatformModel]:
        rows = run_query(
            f"{SELECT_MODEL_SQL} WHERE m.nome ILIKE %s ORDER BY m.nome ASC",
            (f"%{query}%",),
            fetch="all",
        )
        return [PlatformModel(**row) for row in rows]

    def update_code(self, model_id: int, codigo: str) -> bool:
        count = run_query(
            "UPDATE modelosPlataforma SET codigo = %s WHERE id = %s",
            (codigo, model_id),
            fetch="count",
        )
        return count > 0

    def list_by_project(self, project_id: int) -> List[PlatformModel]:
        rows = run_query(
            f"{SELECT_MODEL_SQL} "
            "JOIN projeto_modelos pm ON m.id = pm.modelo_id "
            "WHERE pm.projeto_id = %s ORDER BY m.nome ASC",
            (project_id,),
            fetch="all",
        )
        return [PlatformModel(**row) for row in rows]

    def link_to_project(self, project_id: int, model_id: int) -> None:
        run_query(
            "INSERT INTO projeto_modelos (projeto_id, modelo_id) VALUES (%s, %s) "
            "ON CONFLICT (projeto_id, modelo_id) DO NOTHING",
            (project_id, model_id),
            fetch="count",
        )

    def unlink_from_project(self, project_id: int, model_id: int) -> bool:
        count = run_query(
            "DELETE FROM projeto_modelos WHERE projeto_id = %s AND modelo_id = %s",
            (project_id, model_id),
            fetch="count",
        )
        return count > 0
