# CROSSPLAT IDE

Plataforma web para desenvolvimento multiplataforma baseada em DSL.
Esta entrega implementa os **Requisitos Funcionais RF01 a RF04**.

| RF | Descrição | Endpoint |
|----|-----------|----------|
| RF01 | Cadastro de usuário | `POST /api/auth/register` |
| RF02 | Login com JWT | `POST /api/auth/login` |
| RF03 | Criar projeto (apenas nome) | `POST /api/projects` |
| RF04 | Listar / excluir projetos | `GET /api/projects` · `DELETE /api/projects/{id}` |

**Tecnologias:** React (Vite) · Python/Flask · PostgreSQL · Docker · JWT
**Arquitetura:** Clean Architecture (detalhes em [`backend/README.md`](backend/README.md))

---

## Estrutura

```
crossplat/
├── docker-compose.yml        # Sobe banco, backend e frontend
├── .env.example              # Modelo das variáveis de ambiente
├── docker/postgres/init.sql  # Criação das tabelas
├── backend/                  # API Flask em Clean Architecture
│   ├── app.py                #   Composition root (injeção de dependências)
│   └── src/
│       ├── domain/           #   1. Entidades e interfaces
│       ├── use_cases/        #   2. Casos de uso (RF01–RF04)
│       ├── adapters/         #   3. Controllers, middleware JWT, repositórios
│       └── infrastructure/   #   4. Conexão com banco, hash e JWT
└── frontend/                 # React
    └── src/
        ├── services/api.js       # Axios + token JWT
        ├── context/AuthContext   # Estado de login
        └── pages/                # Login, Register, Dashboard, EditorView
```

---

## 1. Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e **aberto**.
- Git.

Não é necessário instalar Python, Node ou PostgreSQL — tudo roda em containers.

---

## 2. Configuração (apenas na primeira vez)

Na pasta `crossplat`, crie o arquivo `.env` a partir do modelo:

```powershell
copy .env.example .env
```

Abra o `.env` e troque `POSTGRES_PASSWORD` e `JWT_SECRET_KEY`.
Para gerar um segredo aleatório para o JWT:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. Subir a aplicação

```powershell
docker compose up --build
```

Aguarde aparecer `Running on http://0.0.0.0:5000` (backend) e `Local: http://localhost:3000` (frontend).

| Serviço | Endereço |
|---------|----------|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:5000/api/health |
| PostgreSQL | `localhost:5432` |

Para parar: `Ctrl + C` e depois `docker compose down`.
Para apagar também o banco (começar do zero): `docker compose down -v`.

---

## 4. Testar pelo navegador

Acesse http://localhost:3000

| # | Requisito | Passos | Resultado esperado |
|---|-----------|--------|--------------------|
| 1 | RF01 | Clique em **Cadastre-se**, preencha nome, e-mail e senha (≥ 6) | Alerta "Cadastro realizado" e volta ao login |
| 2 | RF01 (erro) | Cadastre de novo o **mesmo e-mail** | Mensagem "Este e-mail já está cadastrado." |
| 3 | RF02 | Faça login com os dados criados | Abre "Meus Projetos" com "Bem-vindo, \<nome\>" |
| 4 | RF02 (erro) | Faça login com senha errada | Mensagem "E-mail ou senha inválidos." |
| 5 | RF03 | Digite um nome e clique **+ Novo Projeto** | Card aparece com a data de hoje |
| 6 | RF04 | Atualize a página (F5) | Projetos continuam listados (vêm do banco) |
| 7 | RF04 | Clique em **Acessar** | Abre a tela do projeto; **← Voltar** retorna |
| 8 | RF04 | Clique em **Excluir** e confirme | Card some |
| 9 | Isolamento | Saia, crie outro usuário e entre | Ele **não vê** os projetos do primeiro |

Para ver o token JWT: `F12` → **Application** → **Local Storage** → `http://localhost:3000` → chave `token`.

---

## 5. Testar a API direto (PowerShell)

Com os containers rodando, em outro terminal:

```powershell
$api = "http://localhost:5000/api"

# RF01 - Cadastro
Invoke-RestMethod -Method Post -Uri "$api/auth/register" -ContentType "application/json" `
  -Body '{"nome":"Teste API","email":"api@teste.com","senha":"123456"}'

# RF02 - Login (guarda o token)
$login = Invoke-RestMethod -Method Post -Uri "$api/auth/login" -ContentType "application/json" `
  -Body '{"email":"api@teste.com","senha":"123456"}'
$headers = @{ Authorization = "Bearer $($login.token)" }

# RF03 - Criar projeto
$proj = Invoke-RestMethod -Method Post -Uri "$api/projects" -Headers $headers -ContentType "application/json" `
  -Body '{"nome":"Projeto via API"}'

# RF04 - Listar
Invoke-RestMethod -Uri "$api/projects" -Headers $headers

# RF04 - Excluir
Invoke-RestMethod -Method Delete -Uri "$api/projects/$($proj.id)" -Headers $headers

# Sem token -> deve retornar 401
Invoke-RestMethod -Uri "$api/projects"
```

---

## 6. Conferir o banco de dados

```powershell
docker compose exec postgres psql -U crossplat -d crossplat_db
```

> Use o usuário/banco definidos no seu `.env` (`POSTGRES_USER` / `POSTGRES_DB`).

Dentro do `psql`:

```sql
\dt                         -- lista as tabelas
SELECT id, nome, email, senha FROM usuarios;   -- a senha aparece como HASH, nunca em texto
SELECT * FROM projetos;
\q                          -- sair
```

---

## 7. Problemas comuns

| Problema | Solução |
|----------|---------|
| `Defina JWT_SECRET_KEY no arquivo .env` | Você não criou o `.env` (passo 2) |
| `port is already allocated` | Outro programa usa a porta 5432/5000/3000. Feche-o ou pare outro PostgreSQL local |
| Erro de senha do banco após mudar o `.env` | O banco já foi criado com a senha antiga: `docker compose down -v` e suba de novo |
| Tabelas não existem | O `init.sql` só roda com banco vazio: `docker compose down -v` |
| Frontend não atualiza | `docker compose up --build` |

