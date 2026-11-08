"""
CAMADA 6 - INFRASTRUCTURE: Repositório de projetos PostgreSQL
Implementa a interface IProjectRepository traduzindo para SQL.
"""
from typing import List, Optional
from src.models.project import Project
from src.repositories.i_project_repository import IProjectRepository
from src.infrastructure.postgres_query_helper import run_query


class PostgresProjectRepositoryAdapter(IProjectRepository):
    def create(self, project: Project) -> Project:
        row = run_query(
            "INSERT INTO projetos (nome, usuario_id) VALUES (%s, %s) "
            "RETURNING id, nome, usuario_id, data_criacao, gpl_code, datatype_def, global_functions, deploy_model",
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

    def find_by_id(self, project_id: int, usuario_id: int) -> Optional[Project]:
        row = run_query(
            "SELECT id, nome, usuario_id, data_criacao, gpl_code, datatype_def, global_functions, deploy_model "
            "FROM projetos WHERE id = %s AND usuario_id = %s",
            (project_id, usuario_id),
        )
        return Project(**row) if row else None

    def update_files(self, project: Project) -> bool:
        count = run_query(
            "UPDATE projetos SET gpl_code = %s, datatype_def = %s, global_functions = %s, deploy_model = %s "
            "WHERE id = %s AND usuario_id = %s",
            (
                project.gpl_code,
                project.datatype_def,
                project.global_functions,
                project.deploy_model,
                project.id,
                project.usuario_id,
            ),
            fetch="count",
        )
        return count > 0

    def delete(self, project_id: int, usuario_id: int) -> bool:
        count = run_query(
            "DELETE FROM projetos WHERE id = %s AND usuario_id = %s",
            (project_id, usuario_id),
            fetch="count",
        )
        return count > 0
