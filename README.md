# CROSSPLAT IDE

IDE web para desenvolvimento e geração de código multiplataforma baseada em DSL/Xtext, sem depender da instalação local do Eclipse.
Esta entrega implementa os **Requisitos Funcionais RF01 a RF10**, estruturando o backend na **Onion Architecture** e o frontend em **React + Monaco Editor**.

---

## 1. Visão Geral e Fluxo de Funcionamento

A **CROSSPLAT IDE** permite criar modelos de software independentes de plataforma e compilá-los para diferentes linguagens e frameworks diretamente pelo navegador:

1. **Autenticação e Workspace (RF01–RF04):** o usuário cria uma conta, realiza login com JWT e gerencia seus projetos no dashboard.
2. **Edição Online com Monaco Editor (RF05–RF06):** dentro de um projeto, o usuário edita os arquivos fonte da DSL:
   - `GPL.crossplat` (`gpl_code`) — classes e lógica independente de plataforma;
   - `datatypes.crossplat` (`datatype_def`) — definições de tipos de dados;
   - `global.crossplat` (`global_functions`) — declarações de funções globais;
   - `deploy.crossplat` (`deploy_model`) — mapeamento entre classes e plataformas alvo.
3. **Marketplace e Criação de Plataformas (RF07–RF08):** o usuário busca e vincula modelos de plataforma da comunidade ou cria seus próprios modelos em uma linguagem base cadastrada (`C++`, `CSharp`, `Dart`, `Java`, `JavaScript`, `Kotlin`, `Python`, `Swift`), com cabeçalho e fechamento protegidos (`platform <nome>: <linguagem> { ... }`).
4. **Painel Visual de Deploy (RF09):** a aba visual lê automaticamente as classes (`class Nome {`) declaradas em `GPL.crossplat` e permite selecionar as plataformas vinculadas para cada classe, gerando o arquivo `deploy.crossplat` em tempo real.
5. **Compilação & Build (RF10):** ao clicar em **Compilar & Build**, o backend cria uma pasta temporária **única para aquele build** (`tempfile.mkdtemp` dentro de `TEMP_BUILD_DIR`), escreve `datatype.crossplat`, `global.crossplat` e concatena `deploy_model + gpl_code + plataformas vinculadas` em `gpl.crossplat`, executa o `generator.jar` via Java e devolve os arquivos gerados da pasta `saida/` para visualização na aba **Output**. Os arquivos gerados são lidos para a memória e a pasta do build é **apagada ao final**, com sucesso, erro ou timeout.

---

## 2. Requisitos Funcionais e Endpoints da API

Todas as rotas protegidas exigem o cabeçalho `Authorization: Bearer <token>`.

| RF | Descrição | Método e Endpoint |
|----|-----------|-------------------|
| RF01 | Cadastro de usuário | `POST /api/auth/register` |
| RF02 | Login com geração de token JWT | `POST /api/auth/login` |
| RF03 | Criar projeto | `POST /api/projects` |
| RF04 | Listar e excluir projetos do usuário | `GET /api/projects` · `DELETE /api/projects/<id>` |
| RF05 | Salvar arquivos do projeto e código de plataforma própria | `PUT /api/projects/<id>` · `PUT /api/marketplace/<model_id>` |
| RF06 | Carregar projeto completo e plataformas vinculadas para o editor | `GET /api/projects/<id>` |
| RF07 | Buscar no Marketplace, vincular e desvincular plataformas | `GET /api/marketplace?q=<busca>` · `POST /api/projects/<id>/link_model` · `DELETE /api/projects/<id>/model/<model_id>` |
| RF08 | Listar linguagens base e criar/atualizar plataforma com template protegido | `GET /api/linguagens` · `POST /api/marketplace` · `PUT /api/marketplace/<model_id>` |
| RF09 | Configurar deploy visualmente e persistir `deploy_model` | `PUT /api/projects/<id>` *(painel visual no frontend a partir de `GPL.crossplat`)* |
| RF10 | Compilar & Build executando `generator.jar` | `POST /api/projects/<id>/build` |
| — | Verificação de saúde da API (Healthcheck) | `GET /api/health` |

---

## 3. Arquitetura do Backend (Onion Architecture)

O backend segue a **Onion Architecture (Arquitetura Cebola)**, organizada em 6 camadas concêntricas dentro de `backend/src/`, tendo [`backend/app.py`](backend/app.py) como **Composition Root**.

### Diagrama dos Anéis Concêntricos

```text
+-------------------------------------------------------------------------+
|  Camada 6: infrastructure/  (PostgreSQL, Werkzeug, PyJWT, generator.jar)|
|  +-------------------------------------------------------------------+  |
|  |  Camada 5: routes/  (Blueprints Flask, HTTP JSON, @auth_required) |  |
|  |  +-------------------------------------------------------------+  |  |
|  |  |  Camada 4: services/  (Casos de uso + i_*.py de serviços)   |  |  |
|  |  |  +-------------------------------------------------------+  |  |  |
|  |  |  |  Camada 3: repositories/  (Interfaces i_*_repository) |  |  |  |
|  |  |  |  +-------------------------------------------------+  |  |  |  |
|  |  |  |  |  Camada 2: schemas/  (DTOs de entrada e saída)  |  |  |  |  |
|  |  |  |  |  +-------------------------------------------+  |  |  |  |  |
|  |  |  |  |  |  Camada 1: models/  (Entidades de domínio)|  |  |  |  |  |
|  |  |  |  |  +-------------------------------------------+  |  |  |  |  |
|  |  |  |  +-------------------------------------------------+  |  |  |  |
|  |  |  +-------------------------------------------------------+  |  |  |
|  |  +-------------------------------------------------------------+  |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
         Composition Root: backend/app.py (conecta todas as camadas)
```

### Regra da Dependência

**Cada camada só pode importar de si própria ou das camadas anteriores (mais internas).** Camadas internas nunca conhecem camadas externas nem detalhes de frameworks ou banco de dados.

### As 6 Camadas e o Composition Root

1. **`models/` (Camada 1 — Núcleo de Domínio)**
   - **Para que serve:** representar as entidades de negócio e suas regras de validação em Python puro.
   - **O que contém:** [`user.py`](backend/src/models/user.py), [`project.py`](backend/src/models/project.py), [`language.py`](backend/src/models/language.py), [`platform_model.py`](backend/src/models/platform_model.py) e [`generated_file.py`](backend/src/models/generated_file.py).
   - **O que NÃO pode fazer:** importar Flask, psycopg2, bibliotecas externas ou qualquer outra camada, nem conter métodos de serialização HTTP como `to_dict()`.

2. **`schemas/` (Camada 2 — Contratos de Entrada e Saída / DTOs)**
   - **Para que serve:** transportar e formatar dados de entrada e saída entre rotas e serviços em dataclasses Python puras, garantindo que dados sensíveis (como `senha`) nunca sejam expostos.
   - **O que contém:** `register_user_schema.py`, `login_schema.py`, `create_project_schema.py`, `update_project_schema.py`, `create_platform_model_schema.py`, `update_platform_model_schema.py`, `link_platform_model_schema.py`, `user_response_schema.py`, `auth_response_schema.py`, `project_response_schema.py`, `project_detail_response_schema.py`, `platform_model_response_schema.py`, `language_response_schema.py` e `build_response_schema.py`.
   - **O que NÃO pode fazer:** importar Flask, psycopg2, `repositories/`, `services/`, `routes/` ou `infrastructure/`.

3. **`repositories/` (Camada 3 — Interfaces de Persistência)**
   - **Para que serve:** definir os contratos abstratos (`ABC`) de acesso a dados que os serviços consomem sem conhecer o banco utilizado.
   - **O que contém:** [`i_user_repository.py`](backend/src/repositories/i_user_repository.py), [`i_project_repository.py`](backend/src/repositories/i_project_repository.py), [`i_platform_model_repository.py`](backend/src/repositories/i_platform_model_repository.py) e [`i_language_repository.py`](backend/src/repositories/i_language_repository.py).
   - **O que NÃO pode fazer:** conter SQL, importar PostgreSQL/`psycopg2` ou depender de `services/`, `routes/` ou `infrastructure/`.

4. **`services/` (Camada 4 — Casos de Uso e Contratos de Serviços)**
   - **Para que serve:** orquestrar as regras de aplicação (RF01 a RF10) e declarar interfaces para serviços externos de infraestrutura.
   - **O que contém:** interfaces `i_password_hasher.py`, `i_token_service.py` e `i_code_generator_service.py`, além dos casos de uso `register_user_service.py`, `authenticate_user_service.py`, `create_project_service.py`, `list_projects_service.py`, `delete_project_service.py`, `get_project_detail_service.py`, `update_project_files_service.py`, `search_platform_models_service.py`, `create_platform_model_service.py`, `update_platform_model_service.py`, `link_platform_model_service.py`, `unlink_platform_model_service.py`, `list_languages_service.py` e `build_project_service.py`.
   - **O que NÃO pode fazer:** importar `flask`, `psycopg2`, `jwt`, `werkzeug`, `routes/` ou `infrastructure/`.

5. **`routes/` (Camada 5 — Controladores HTTP Flask e Middleware)**
   - **Para que serve:** receber requisições HTTP, extrair o JSON para um schema, delegar ao service e retornar `jsonify(...)` com o status HTTP adequado.
   - **O que contém:** [`auth_middleware.py`](backend/src/routes/auth_middleware.py), [`auth_routes.py`](backend/src/routes/auth_routes.py), [`project_routes.py`](backend/src/routes/project_routes.py), [`marketplace_routes.py`](backend/src/routes/marketplace_routes.py) e [`language_routes.py`](backend/src/routes/language_routes.py).
   - **O que NÃO pode fazer:** conter lógica de negócio ou SQL, nem importar `models/`, `repositories/` ou `infrastructure/`.

6. **`infrastructure/` (Camada 6 — Implementações Concretas Externas)**
   - **Para que serve:** implementar as interfaces das camadas internas conectando a aplicação ao PostgreSQL, Werkzeug, PyJWT e ao processo Java do compilador Xtext.
   - **O que contém:** [`postgres_connection.py`](backend/src/infrastructure/postgres_connection.py), [`postgres_query_helper.py`](backend/src/infrastructure/postgres_query_helper.py), [`postgres_user_repository_adapter.py`](backend/src/infrastructure/postgres_user_repository_adapter.py), [`postgres_project_repository_adapter.py`](backend/src/infrastructure/postgres_project_repository_adapter.py), [`postgres_platform_model_repository_adapter.py`](backend/src/infrastructure/postgres_platform_model_repository_adapter.py), [`postgres_language_repository_adapter.py`](backend/src/infrastructure/postgres_language_repository_adapter.py), [`werkzeug_password_hasher_service.py`](backend/src/infrastructure/werkzeug_password_hasher_service.py), [`jwt_token_service.py`](backend/src/infrastructure/jwt_token_service.py) e [`java_code_generator_service.py`](backend/src/infrastructure/java_code_generator_service.py).
   - **O que NÃO pode fazer:** ser importada pelas camadas internas (`models/`, `schemas/`, `repositories/`, `services/`, `routes/`).

- **`backend/app.py` (Composition Root):** único ponto do sistema que importa todas as camadas. Na inicialização (`create_app`), chama `ensure_schema()`, instancia os adapters de `infrastructure/`, injeta-os nos `services/`, registra os blueprints de `routes/` no Flask e expõe `GET /api/health`.

### Por que existem as interfaces (`i_*.py`) e por que o gerador Java fica na infraestrutura?

- **Inversão de Dependência (`i_*.py`):** os casos de uso em `services/` dependem apenas de abstrações (`IUserRepository`, `IProjectRepository`, `IPasswordHasher`, `ITokenService`, etc.), e não das bibliotecas concretas. Isso permite trocar o PostgreSQL por outro banco ou substituir `Werkzeug`/`PyJWT` por outra biblioteca de criptografia apenas criando uma nova classe em `infrastructure/`, sem alterar nenhuma linha dos `services/`.
- **Por que o gerador Java fica atrás de [`ICodeGeneratorService`](backend/src/services/i_code_generator_service.py) em `infrastructure/`:** criar pastas temporárias no disco, gravar arquivos `.crossplat`, invocar `subprocess.run(["java", "-jar", ...])` e varrer o diretório `saida/` são operações dependentes de sistema operacional e linha de comando. Mantendo apenas o contrato `ICodeGeneratorService` na camada de serviços e a execução concreta em [`JavaCodeGeneratorService`](backend/src/infrastructure/java_code_generator_service.py), o caso de uso [`BuildProjectService`](backend/src/services/build_project_service.py) fica isolado de detalhes de SO/JVM e fácil de testar.

### Exemplo do Caminho de uma Requisição (Criar Projeto — RF03)

```text
POST /api/projects {"nome": "AppIoT"}
  │
  ▼
project_routes.py (routes)
  ├─ valida token JWT via make_auth_required (auth_middleware.py) -> define g.user_id
  └─ instancia CreateProjectSchema(nome=data.get("nome"))
  │
  ▼
CreateProjectService.execute(schema, g.user_id) (services)
  ├─ instancia Project(...) e executa project.validate() (models)
  └─ chama self.projects.create(project) pela interface IProjectRepository (repositories)
  │
  ▼
PostgresProjectRepositoryAdapter.create(project) (infrastructure)
  └─ executa INSERT INTO projetos ... via run_query (postgres_query_helper.py)
  │
  ▼
PostgreSQL ──► retorna registro ──► ProjectResponseSchema.from_model(...) ──► HTTP 201 JSON
```

---

## 4. Estrutura de Pastas do Projeto

```text
crossplat/
├── .env.example                                              # Modelo das variáveis de ambiente
├── .gitignore
├── docker-compose.yml                                        # Orquestra postgres, backend e frontend
├── README.md
├── backend/                                                  # API Flask em Onion Architecture
│   ├── Dockerfile                                            # Python 3.11 + default-jre-headless (Java para RF10)
│   ├── README.md                                             # Mapa detalhado das camadas do backend
│   ├── requirements.txt                                      # Flask, Flask-Cors, psycopg2-binary, PyJWT
│   ├── requirements-dev.txt                                  # pytest (dependência só para testes)
│   ├── pytest.ini                                            # Configuração do pytest (pythonpath e pasta tests/)
│   ├── app.py                                                # Composition Root + GET /api/health
│   ├── tests/                                                # Testes automatizados (pytest)
│   │   ├── conftest.py                                       # Repositórios e serviços FALSOS em memória
│   │   ├── test_architecture.py                              # Regra da dependência entre as camadas
│   │   ├── test_auth.py                                      # RF01 e RF02
│   │   ├── test_platforms.py                                 # RF07 e RF08
│   │   └── test_projects.py                                  # RF03 a RF06 e RF10
│   └── src/
│       ├── models/                                           # Camada 1: Entidades de domínio
│       │   ├── user.py
│       │   ├── project.py
│       │   ├── language.py
│       │   ├── platform_model.py
│       │   └── generated_file.py
│       ├── schemas/                                          # Camada 2: DTOs de entrada e saída
│       │   ├── register_user_schema.py
│       │   ├── login_schema.py
│       │   ├── create_project_schema.py
│       │   ├── update_project_schema.py
│       │   ├── create_platform_model_schema.py
│       │   ├── update_platform_model_schema.py
│       │   ├── link_platform_model_schema.py
│       │   ├── user_response_schema.py
│       │   ├── auth_response_schema.py
│       │   ├── project_response_schema.py
│       │   ├── project_detail_response_schema.py
│       │   ├── platform_model_response_schema.py
│       │   ├── language_response_schema.py
│       │   └── build_response_schema.py
│       ├── repositories/                                     # Camada 3: Interfaces de repositório
│       │   ├── i_user_repository.py
│       │   ├── i_project_repository.py
│       │   ├── i_platform_model_repository.py
│       │   └── i_language_repository.py
│       ├── services/                                         # Camada 4: Casos de uso e interfaces de serviço
│       │   ├── i_password_hasher.py
│       │   ├── i_token_service.py
│       │   ├── i_code_generator_service.py
│       │   ├── register_user_service.py
│       │   ├── authenticate_user_service.py
│       │   ├── create_project_service.py
│       │   ├── list_projects_service.py
│       │   ├── delete_project_service.py
│       │   ├── get_project_detail_service.py
│       │   ├── update_project_files_service.py
│       │   ├── search_platform_models_service.py
│       │   ├── create_platform_model_service.py
│       │   ├── update_platform_model_service.py
│       │   ├── link_platform_model_service.py
│       │   ├── unlink_platform_model_service.py
│       │   ├── list_languages_service.py
│       │   └── build_project_service.py
│       ├── routes/                                           # Camada 5: Rotas HTTP Flask e middleware
│       │   ├── auth_middleware.py
│       │   ├── auth_routes.py
│       │   ├── project_routes.py
│       │   ├── marketplace_routes.py
│       │   └── language_routes.py
│       └── infrastructure/                                   # Camada 6: PostgreSQL, JWT, Werkzeug e JAR Java
│           ├── postgres_connection.py
│           ├── postgres_query_helper.py
│           ├── postgres_user_repository_adapter.py
│           ├── postgres_project_repository_adapter.py
│           ├── postgres_platform_model_repository_adapter.py
│           ├── postgres_language_repository_adapter.py
│           ├── werkzeug_password_hasher_service.py
│           ├── jwt_token_service.py
│           └── java_code_generator_service.py
├── frontend/                                                 # SPA React + Vite + Monaco Editor
│   ├── Dockerfile
│   ├── index.html                                            # Carrega Google Fonts, Material Symbols e Monaco AMD
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── context/AuthContext.jsx
│       ├── services/api.js                                   # Cliente Axios com interceptor JWT
│       └── pages/
│           ├── Login.jsx
│           ├── Register.jsx
│           ├── Dashboard.jsx
│           └── EditorView.jsx                                # IDE online, Marketplace, Deploy visual e Build
├── docker/
│   └── postgres/
│       └── init.sql                                          # DDL inicial e seed de linguagens
├── generator/                                                # Pasta montada em /generator no container backend
│   ├── README.md
│   └── generator.jar                                         # Compilador Xtext usado no RF10
└── docs/                                                     # Documentação e protótipos do projeto
    ├── 1.pdf
    ├── prot_tipo_do_sistema.html
    └── reqisitos.pdf
```

---

## 5. Banco de Dados (PostgreSQL)

O schema definido em [`docker/postgres/init.sql`](docker/postgres/init.sql) (e garantido na inicialização do backend por `ensure_schema()`) possui **5 tabelas**:

1. **`usuarios`**: contas de usuários (`id`, `nome`, `email`, `senha`, `data_criacao`).
2. **`projetos`**: projetos do usuário e seus 4 arquivos fonte (`id`, `nome`, `usuario_id`, `gpl_code`, `datatype_def`, `global_functions`, `deploy_model`, `data_criacao`).
3. **`linguagens`**: linguagens alvo disponíveis para plataformas (`id`, `nome` — pré-populada com `C++`, `CSharp`, `Dart`, `Java`, `JavaScript`, `Kotlin`, `Python`, `Swift`).
4. **`modelosPlataforma`**: modelos de plataforma publicados no Marketplace (`id`, `nome`, `codigo`, `criador_id`, `linguagem_id`, `data_criacao`).
5. **`projeto_modelos`**: tabela associativa N:N entre projetos e plataformas vinculadas (`projeto_id`, `modelo_id`).

### Diagrama de Relações

```text
  +--------------+        1:N        +------------------------------------+
  |   usuarios   |------------------>|              projetos              |
  +--------------+                   +------------------------------------+
         |                             ^
         | 1:N (criador_id)            | N:M (via projeto_modelos)
         v                             v
  +-------------------+      N:1     +------------------------------------+
  | modelosPlataforma |------------->|          projeto_modelos           |
  +-------------------+              |   (projeto_id FK, modelo_id FK)    |
         |                           +------------------------------------+
         | N:1 (linguagem_id, ON DELETE SET NULL)
         v
  +--------------+
  |  linguagens  |
  +--------------+
```

### Como Acessar via Terminal (`psql`)

Use os valores configurados no seu arquivo `.env` (`POSTGRES_USER` e `POSTGRES_DB`):

```powershell
docker compose exec postgres psql -U <usuario> -d <banco>
```

Com o `.env.example` padrão, por exemplo: `docker compose exec postgres psql -U crossplat -d crossplat_db`.

Comandos úteis dentro do `psql`:

```sql
\dt                                             -- lista todas as 5 tabelas
\d projetos                                     -- mostra colunas, tipos e FKs de projetos
SELECT id, nome, email, senha FROM usuarios;    -- confirma que a senha está salva como hash
```

> ℹ️ **Nota:** a tabela é criada como `modelosPlataforma` sem aspas, então o PostgreSQL grava o nome em minúsculas (`modelosplataforma`). No `psql`, `\dt` mostra `modelosplataforma`; consultas sem aspas (`SELECT * FROM modelosPlataforma;`) funcionam, mas com aspas o nome precisa estar em minúsculas (`"modelosplataforma"`).

> ⚠️ **Atenção:** executar `docker compose down -v` remove o volume `pgdata` e **apaga permanentemente todos os dados** do banco de dados.

---

## 6. Como Executar

### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e **aberto**.
- Git.
- Arquivo **`generator/generator.jar`** presente na pasta `generator/` (necessário para o **Build — RF10**; a pasta `./generator` é montada em `/generator` dentro do container `backend`).

Não é necessário instalar Python, Node, Java ou PostgreSQL na máquina host — o Java JRE (`default-jre-headless`) já é instalado automaticamente pelo [`backend/Dockerfile`](backend/Dockerfile).

### Configuração (apenas na primeira vez)

Na raiz `crossplat/`, crie o arquivo `.env` a partir do modelo:

```powershell
copy .env.example .env
```

Abra o `.env` e troque `POSTGRES_PASSWORD` e `JWT_SECRET_KEY`.
Para gerar um segredo aleatório para o JWT:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

### Subir a Aplicação

```powershell
docker compose up --build
```

Aguarde aparecer `Running on http://0.0.0.0:5000` (backend) e `Local: http://localhost:3000` (frontend).

| Serviço | Endereço |
|---------|----------|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:5000/api/health |
| PostgreSQL | `localhost:5432` |

Para parar mantendo os dados: `Ctrl + C` e depois `docker compose down`.
Para parar e apagar também os dados do banco: `docker compose down -v`.

---

## 7. Tecnologias Utilizadas

- **Frontend:** React (Vite), Monaco Editor (carregado via CDN em [`frontend/index.html`](frontend/index.html)) e Axios.
- **Backend:** Python 3.11 com Flask, Flask-Cors, PyJWT e Werkzeug.
- **Compilação / Geração de Código:** Java (`default-jre-headless`) executando `generator.jar` (Xtext).
- **Banco de Dados:** PostgreSQL 16 (`psycopg2-binary`).
- **Infraestrutura e Autenticação:** Docker / Docker Compose e JWT (Bearer Token).
- **Testes:** pytest.

---

## 8. Segurança

- **Senhas com hash:** [`WerkzeugPasswordHasherService`](backend/src/infrastructure/werkzeug_password_hasher_service.py) gera hash no `RegisterUserService`; a senha nunca é retornada nas respostas da API ([`UserResponseSchema`](backend/src/schemas/user_response_schema.py)).
- **Autenticação JWT:** tokens assinados com `HS256` ([`JwtTokenService`](backend/src/infrastructure/jwt_token_service.py)) e exigidos pelo middleware `@auth_required` em todas as rotas de projetos, marketplace e linguagens.
- **Isolamento de dono:** consultas, edições, vínculos e builds filtram por `usuario_id` do token (`WHERE id = %s AND usuario_id = %s`), e apenas o `criador_id` pode alterar o código de um modelo de plataforma.
- **Build em diretório temporário:** cada compilação ocorre em uma pasta única criada com `tempfile.mkdtemp` dentro de `TEMP_BUILD_DIR` (`/tmp/crossplat_builds` no `docker-compose.yml`), o que isola builds simultâneos. A pasta é removida no `finally` de [`JavaCodeGeneratorService`](backend/src/infrastructure/java_code_generator_service.py), com sucesso, erro ou timeout, então o código do usuário não fica no disco. A execução do `generator.jar` tem timeout de 30 segundos.

---

## 9. Testes

### Como rodar

Localmente (requer Python 3.11):

```powershell
cd backend
pip install -r requirements-dev.txt
python -m pytest
```

Via Docker, com a aplicação rodando (`docker compose up`):

```powershell
docker compose exec backend pip install -r requirements-dev.txt
docker compose exec backend python -m pytest
```

### O que é testado

- **Regras de negócio dos services (RF01 a RF08 e RF10):** [`test_auth.py`](backend/tests/test_auth.py) (RF01 e RF02), [`test_projects.py`](backend/tests/test_projects.py) (RF03 a RF06 e RF10) e [`test_platforms.py`](backend/tests/test_platforms.py) (RF07 e RF08) chamam os services diretamente.
- **Sem PostgreSQL, Docker nem `generator.jar`:** [`conftest.py`](backend/tests/conftest.py) fornece repositórios e serviços **falsos em memória** (`FakeUserRepository`, `FakeProjectRepository`, `FakePlatformModelRepository`, `FakeLanguageRepository`, `FakePasswordHasher`, `FakeTokenService` e `FakeCodeGenerator`). Isso só é possível porque os services dependem de interfaces (`i_*.py`) e não das implementações concretas (inversão de dependência): os testes injetam os falsos no lugar dos adapters de `infrastructure/`.
- **Arquitetura:** [`test_architecture.py`](backend/tests/test_architecture.py) lê os imports de cada arquivo de `src/` e falha se uma camada importar de uma camada mais externa (fora da sua lista permitida) ou se o núcleo (`models/`, `schemas/`, `repositories/`, `services/`) usar `flask`, `psycopg2`, `jwt`, `werkzeug`, `requests` ou `subprocess`.

### O que NÃO é testado

As rotas HTTP, o SQL real no PostgreSQL, o `generator.jar` e o frontend não têm testes automatizados; são validados manualmente.

---

## 10. Decisões de Arquitetura e Próximos Passos

- **Redis / cache: não adotado.** O estado do editor já fica no React (digitar não gera requisição), cada ação faz no máximo 3 consultas ao banco e o resultado do build não se repete o suficiente para compensar um cache.
- **Worker / fila para o build: não adotado.** Builds de projetos diferentes não conflitam, pois cada build tem sua própria pasta; a escala esperada é pequena.
- **Pool de conexões: melhoria futura (issue #17).** Hoje `run_query` ([`postgres_query_helper.py`](backend/src/infrastructure/postgres_query_helper.py)) abre uma conexão nova por consulta. A mudança fica restrita à camada `infrastructure/`, sem alterar `services/` nem `routes/`.
- **Gunicorn + Nginx: planejados para produção.** Hoje a aplicação usa o servidor de desenvolvimento do Flask.

Como os services dependem apenas de interfaces, cada item acima pode ser adicionado criando uma nova classe em `infrastructure/` (por exemplo, uma interface `ICacheService` em `services/` com uma implementação Redis em `infrastructure/`) e injetando-a em [`backend/app.py`](backend/app.py), sem alterar a lógica dos services existentes.

---

## 11. Limitações Conhecidas

- [`backend/app.py`](backend/app.py) executa com `debug=True` e `host="0.0.0.0"` (modo de desenvolvimento).
- Um corpo JSON que não é objeto (por exemplo, uma lista) retorna erro 500 nas rotas que usam `request.get_json() or {}`.
- `ensure_schema()` ignora silenciosamente qualquer erro na inicialização (`except Exception: pass` em `create_app`).
- O endpoint de build (`POST /api/projects/<id>/build`) devolve a mensagem da exceção no campo `detalhes` nos erros internos.
- Não há salvamento automático: o editor salva só no botão **Salvar** e antes do **Build**, sem aviso de alterações não salvas.
- Não há pool de conexões, nem CI automático.

---

## 12. Fluxo de Contribuição

1. Cada issue tem uma branch própria criada a partir do `main`, com prefixo pelo tipo: `docs/...`, `fix/...`, `feat/...` ou `test/...` (ex.: `fix/16-limpeza-pasta-build`).
2. As alterações entram em um commit descritivo.
3. Abre-se um Pull Request para o `main` com `Closes #N` na descrição, para que a issue feche sozinha no merge.
4. O Pull Request fica como **Draft** até estar pronto para revisão.
