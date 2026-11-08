"""
CAMADA 3 - ADAPTERS (saída): Helper de consultas PostgreSQL
Função utilitária usada pelos repositórios para executar SQL.
"""
from src.infrastructure.postgres_connection import get_connection


def run_query(sql: str, params: tuple = (), fetch: str = "one"):
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

