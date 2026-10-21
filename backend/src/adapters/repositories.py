"""
CAMADA 3 - ADAPTERS (saída): Repositórios PostgreSQL
Implementam as interfaces do domínio traduzindo para SQL.
"""
from typing import List, Optional
from src.domain.entities import User, Project
from src.domain.interfaces import UserRepository, ProjectRepository
from src.infrastructure.database import get_connection


def _run(sql: str, params: tuple = (), fetch: str = "one"):
    """Executa uma query e retorna uma linha, todas as linhas ou o nº de linhas afetadas."""
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()
            return cur.rowcount
    finally:
        conn.close()


class PostgresUserRepository(UserRepository):
    def create(self, user: User) -> User:
        row = _run(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s) "
            "RETURNING id, nome, email, senha, data_criacao",
            (user.nome, user.email, user.senha),
        )
        return User(**row)

    def find_by_email(self, email: str) -> Optional[User]:
        row = _run("SELECT id, nome, email, senha, data_criacao FROM usuarios WHERE email = %s", (email,))
        return User(**row) if row else None


class PostgresProjectRepository(ProjectRepository):
    def create(self, project: Project) -> Project:
        row = _run(
            "INSERT INTO projetos (nome, usuario_id) VALUES (%s, %s) "
            "RETURNING id, nome, usuario_id, data_criacao",
            (project.nome, project.usuario_id),
        )
        return Project(**row)

    def list_by_user(self, usuario_id: int) -> List[Project]:
        rows = _run(
            "SELECT id, nome, usuario_id, data_criacao FROM projetos "
            "WHERE usuario_id = %s ORDER BY data_criacao DESC",
            (usuario_id,),
            fetch="all",
        )
        return [Project(**row) for row in rows]

    def delete(self, project_id: int, usuario_id: int) -> bool:
        count = _run(
            "DELETE FROM projetos WHERE id = %s AND usuario_id = %s",
            (project_id, usuario_id),
            fetch="count",
        )
        return count > 0
