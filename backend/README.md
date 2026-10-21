# Backend – Clean Architecture

```
backend/
├── app.py                     # Composition Root: cria as implementações e injeta nos casos de uso
└── src/
    ├── domain/                # CAMADA 1 – Entidades e interfaces (Python puro)
    │   ├── entities.py        #   User, Project
    │   └── interfaces.py      #   UserRepository, ProjectRepository, PasswordHasher, TokenService
    ├── use_cases/             # CAMADA 2 – Regras da aplicação (RF01–RF04)
    │   └── use_cases.py
    ├── adapters/              # CAMADA 3 – Tradução entre o mundo externo e os casos de uso
    │   ├── controllers.py     #   HTTP -> caso de uso -> HTTP
    │   ├── middleware.py      #   Validação do JWT
    │   └── repositories.py    #   Caso de uso -> SQL (PostgreSQL)
    └── infrastructure/        # CAMADA 4 – Detalhes técnicos
        ├── database.py        #   Conexão psycopg2
        └── security.py        #   Hash de senha (Werkzeug) e JWT (PyJWT)
```

## Regra da Dependência

```
infrastructure / adapters  ──►  use_cases  ──►  domain
```

- `domain` não importa nada do projeto.
- `use_cases` importa **somente** `domain` (as interfaces). Não conhece Flask, SQL ou JWT.
- `adapters` e `infrastructure` implementam as interfaces do domínio.
- `app.py` é o único arquivo que junta tudo (injeção de dependência).

Para provar: troque o PostgreSQL por outro banco criando um novo repositório que implemente
`UserRepository` / `ProjectRepository` e altere **apenas** `app.py`.
