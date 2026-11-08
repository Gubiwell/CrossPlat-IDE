-- Script de Inicialização do PostgreSQL para a CROSSPLAT IDE
-- Requisitos Funcionais RF01 a RF10

-- ── Módulo de Usuários (RF01, RF02) ──────────────────────────
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ── Módulo de Projetos e Arquivos (RF03, RF04, RF05, RF06, RF09) ──
CREATE TABLE IF NOT EXISTS projetos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    gpl_code TEXT NOT NULL DEFAULT '',
    datatype_def TEXT NOT NULL DEFAULT '',
    global_functions TEXT NOT NULL DEFAULT '',
    deploy_model TEXT NOT NULL DEFAULT '',
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Garante que colunas existam caso a tabela projetos tenha sido criada na fase RF01-RF04
ALTER TABLE projetos ADD COLUMN IF NOT EXISTS gpl_code TEXT NOT NULL DEFAULT '';
ALTER TABLE projetos ADD COLUMN IF NOT EXISTS datatype_def TEXT NOT NULL DEFAULT '';
ALTER TABLE projetos ADD COLUMN IF NOT EXISTS global_functions TEXT NOT NULL DEFAULT '';
ALTER TABLE projetos ADD COLUMN IF NOT EXISTS deploy_model TEXT NOT NULL DEFAULT '';

-- ── Módulo de Linguagens e Marketplace de Plataformas (RF07, RF08) ──
CREATE TABLE IF NOT EXISTS linguagens (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE
);

INSERT INTO linguagens (nome) VALUES
    ('C++'),
    ('CSharp'),
    ('Dart'),
    ('Java'),
    ('JavaScript'),
    ('Kotlin'),
    ('Python'),
    ('Swift')
ON CONFLICT (nome) DO NOTHING;

CREATE TABLE IF NOT EXISTS modelosPlataforma (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(150) NOT NULL UNIQUE,
    codigo TEXT NOT NULL,
    criador_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    linguagem_id INTEGER REFERENCES linguagens(id) ON DELETE SET NULL,
    data_criacao TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS projeto_modelos (
    projeto_id INTEGER NOT NULL REFERENCES projetos(id) ON DELETE CASCADE,
    modelo_id INTEGER NOT NULL REFERENCES modelosPlataforma(id) ON DELETE CASCADE,
    PRIMARY KEY (projeto_id, modelo_id)
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_projetos_usuario_id ON projetos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_modelos_nome ON modelosPlataforma(nome);
