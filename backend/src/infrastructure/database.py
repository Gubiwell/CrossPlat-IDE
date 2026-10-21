"""
CAMADA 4 - INFRAESTRUTURA: Conexão com PostgreSQL
As tabelas são criadas pelo script docker/postgres/init.sql.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)
