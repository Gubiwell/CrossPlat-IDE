"""
CAMADA 6 - INFRASTRUCTURE: Conexão e Migração Automática com PostgreSQL
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_connection():
    return psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)


def ensure_schema() -> None:
    """Garante que as colunas e tabelas dos RF05 a RF10 existam mesmo em volumes antigos."""
    ddl = """
    ALTER TABLE projetos ADD COLUMN IF NOT EXISTS gpl_code TEXT NOT NULL DEFAULT '';
    ALTER TABLE projetos ADD COLUMN IF NOT EXISTS datatype_def TEXT NOT NULL DEFAULT '';
    ALTER TABLE projetos ADD COLUMN IF NOT EXISTS global_functions TEXT NOT NULL DEFAULT '';
    ALTER TABLE projetos ADD COLUMN IF NOT EXISTS deploy_model TEXT NOT NULL DEFAULT '';

    CREATE TABLE IF NOT EXISTS linguagens (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL UNIQUE
    );

    UPDATE linguagens SET nome = 'CSharp' WHERE nome = 'C#';

    INSERT INTO linguagens (nome) VALUES
        ('C++'), ('CSharp'), ('Dart'), ('Java'),
        ('JavaScript'), ('Kotlin'), ('Python'), ('Swift')
    ON CONFLICT (nome) DO NOTHING;

    CREATE TABLE IF NOT EXISTS modelosPlataforma (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(150) NOT NULL UNIQUE,
        codigo TEXT NOT NULL,
        criador_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
        linguagem_id INTEGER REFERENCES linguagens(id) ON DELETE SET NULL,
        data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    UPDATE modelosPlataforma
       SET codigo = REPLACE(codigo, ': C#', ': CSharp')
     WHERE codigo LIKE '%: C#%';

    CREATE TABLE IF NOT EXISTS projeto_modelos (
        projeto_id INTEGER NOT NULL REFERENCES projetos(id) ON DELETE CASCADE,
        modelo_id INTEGER NOT NULL REFERENCES modelosPlataforma(id) ON DELETE CASCADE,
        PRIMARY KEY (projeto_id, modelo_id)
    );
    """
    conn = get_connection()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(ddl)
    finally:
        conn.close()
