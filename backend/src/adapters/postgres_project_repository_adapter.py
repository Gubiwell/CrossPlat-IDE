"""
CAMADA 3 - ADAPTERS (saída): Repositório de projetos PostgreSQL
Implementa a porta ProjectRepositoryPort do domínio traduzindo para SQL.
"""
from typing import List
from src.domain.project_entity import Project
from src.domain.project_repository_port import ProjectRepositoryPort
from src.adapters.postgres_query_helper import run_query


class PostgresProjectRepositoryAdapter(ProjectRepositoryPort):
    def create(self, project: Project) -> Project:
        row = run_query(
            "INSERT INTO projetos (nome, usuario_id) VALUES (%s, %s) "
            "RETURNING id, nome, usuario_id, data_criacao",
            (project.nome, project.usuario_id),
        )
        return Project(**row)

    def list_by_user(self, usuario_id: int) -> List[Project]:
        rows = run_query(
            "SELECT id, nome, usuario_id, data_criacao FROM projetos "
            "WHERE usuario_id = %s ORDER BY data_criacao DESC",
            (usuario_id,),
            fetch="all",
        )
        return [Project(**row) for row in rows]

    def delete(self, project_id: int, usuario_id: int) -> bool:
        count = run_query(
            "DELETE FROM projetos WHERE id = %s AND usuario_id = %s",
            (project_id, usuario_id),
            fetch="count",
        )
        return count > 0

