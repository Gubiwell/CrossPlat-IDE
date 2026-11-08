"""
CAMADA 6 - INFRASTRUCTURE: Repositório de usuários PostgreSQL
Implementa a interface IUserRepository traduzindo para SQL.
"""
from typing import Optional
from src.models.user import User
from src.repositories.i_user_repository import IUserRepository
from src.infrastructure.postgres_query_helper import run_query


class PostgresUserRepositoryAdapter(IUserRepository):
    def create(self, user: User) -> User:
        row = run_query(
            "INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s) "
            "RETURNING id, nome, email, senha, data_criacao",
            (user.nome, user.email, user.senha),
        )
        return User(**row)

    def find_by_email(self, email: str) -> Optional[User]:
        row = run_query("SELECT id, nome, email, senha, data_criacao FROM usuarios WHERE email = %s", (email,))
        return User(**row) if row else None
