"""
CAMADA 3 - ADAPTERS (saída): Repositório de usuários PostgreSQL
Implementa a porta UserRepositoryPort do domínio traduzindo para SQL.
"""
from typing import Optional
from src.domain.user_entity import User
from src.domain.user_repository_port import UserRepositoryPort
from src.adapters.postgres_query_helper import run_query


class PostgresUserRepositoryAdapter(UserRepositoryPort):
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

