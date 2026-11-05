# Backend – Clean Architecture

```
backend/
├── app.py                                   # Composition Root: cria as implementações e injeta nos serviços
└── src/
    ├── domain/                              # CAMADA 1 – Entidades e portas (Python puro)
    │   ├── user_entity.py                   #   User
    │   ├── project_entity.py                #   Project
    │   ├── user_repository_port.py          #   UserRepositoryPort
    │   ├── project_repository_port.py       #   ProjectRepositoryPort
    │   ├── password_hasher_port.py          #   PasswordHasherPort
    │   └── token_service_port.py            #   TokenServicePort
    ├── use_cases/                           # CAMADA 2 – Regras da aplicação (RF01–RF04)
    │   ├── register_user_service.py         #   RF01
    │   ├── authenticate_user_service.py     #   RF02
    │   ├── create_project_service.py        #   RF03
    │   ├── list_projects_service.py         #   RF04
    │   └── delete_project_service.py        #   RF04
    ├── adapters/                            # CAMADA 3 – Tradução entre o mundo externo e os serviços
    │   ├── auth_controller.py               #   HTTP -> serviço -> HTTP (RF01, RF02)
    │   ├── project_controller.py            #   HTTP -> serviço -> HTTP (RF03, RF04)
    │   ├── auth_middleware.py               #   Validação do JWT
    │   ├── postgres_query_helper.py         #   run_query (executa SQL)
    │   ├── postgres_user_repository_adapter.py
    │   └── postgres_project_repository_adapter.py
    └── infrastructure/                      # CAMADA 4 – Detalhes técnicos
        ├── postgres_connection.py           #   Conexão psycopg2
        ├── werkzeug_password_hasher_service.py  # Hash de senha (Werkzeug)
        └── jwt_token_service.py             #   JWT (PyJWT)
```

## Sufixos

| Sufixo | Papel |
|--------|-------|
| `_entity` | Entidade de domínio |
| `_port` | Contrato (interface) definido pelo domínio |
| `_service` (use_cases) | Caso de uso |
| `_adapter` | Implementação de uma porta na camada de adapters |
| `_service` (infrastructure) | Implementação de uma porta usando biblioteca externa |
| `_controller` / `_middleware` | Entrada HTTP |

## Regra da Dependência

```
infrastructure / adapters  ──►  use_cases  ──►  domain
```

- `domain` não importa nada do projeto nem bibliotecas externas.
- `use_cases` importa **somente** `domain` (as portas). Não conhece Flask, SQL ou JWT.
- `adapters` e `infrastructure` implementam as portas do domínio.
- `app.py` é o único arquivo que junta tudo (injeção de dependência).

Para provar: troque o PostgreSQL por outro banco criando um novo adapter que implemente
`UserRepositoryPort` / `ProjectRepositoryPort` e altere **apenas** `app.py`.
