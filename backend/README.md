# Backend — CROSSPLAT IDE (Onion Architecture)

Este backend segue a **Onion Architecture (Arquitetura Cebola)** com a regra da dependência estrita:
**cada camada só importa das camadas anteriores (mais internas)**.

```
Models -> Schemas -> Repositories -> Services -> Routes -> Infrastructure
```

## Estrutura de Pastas (`src/`)

```text
backend/
├── app.py                                           # Composition Root (injeta todas as dependências)
└── src/
    ├── models/                                      # Camada 1: Entidades e validações de domínio (Python puro)
    │   ├── user.py                                  # User (RF01, RF02)
    │   ├── project.py                               # Project com gpl_code, datatype_def, global_functions, deploy_model (RF03–RF09)
    │   ├── language.py                              # Language (RF08)
    │   ├── platform_model.py                        # PlatformModel + validação de estrutura protegida (RF07, RF08)
    │   └── generated_file.py                        # GeneratedFile (RF10)
    ├── schemas/                                     # Camada 2: DTOs de entrada e saída (Python puro + models)
    │   ├── register_user_schema.py                  # RegisterUserSchema
    │   ├── login_schema.py                          # LoginSchema
    │   ├── create_project_schema.py                 # CreateProjectSchema
    │   ├── update_project_schema.py                 # UpdateProjectSchema (RF05, RF09)
    │   ├── create_platform_model_schema.py          # CreatePlatformModelSchema (RF08)
    │   ├── update_platform_model_schema.py          # UpdatePlatformModelSchema (RF05, RF08)
    │   ├── link_platform_model_schema.py            # LinkPlatformModelSchema (RF07)
    │   ├── user_response_schema.py                  # UserResponseSchema (nunca expõe senha)
    │   ├── auth_response_schema.py                  # AuthResponseSchema
    │   ├── project_response_schema.py               # ProjectResponseSchema
    │   ├── project_detail_response_schema.py        # ProjectDetailResponseSchema (RF06)
    │   ├── platform_model_response_schema.py        # PlatformModelResponseSchema (RF07, RF08)
    │   ├── language_response_schema.py              # LanguageResponseSchema (RF08)
    │   └── build_response_schema.py                 # BuildResponseSchema (RF10)
    ├── repositories/                                # Camada 3: Interfaces (contratos) de persistência
    │   ├── i_user_repository.py                     # IUserRepository
    │   ├── i_project_repository.py                  # IProjectRepository
    │   ├── i_platform_model_repository.py           # IPlatformModelRepository
    │   └── i_language_repository.py                 # ILanguageRepository
    ├── services/                                    # Camada 4: Casos de uso e interfaces de serviços
    │   ├── i_password_hasher.py                     # IPasswordHasher
    │   ├── i_token_service.py                       # ITokenService
    │   ├── i_code_generator_service.py              # ICodeGeneratorService (RF10)
    │   ├── register_user_service.py                 # RegisterUserService (RF01)
    │   ├── authenticate_user_service.py             # AuthenticateUserService (RF02)
    │   ├── create_project_service.py                # CreateProjectService (RF03)
    │   ├── list_projects_service.py                 # ListProjectsService (RF04)
    │   ├── delete_project_service.py                # DeleteProjectService (RF04)
    │   ├── get_project_detail_service.py            # GetProjectDetailService (RF06)
    │   ├── update_project_files_service.py          # UpdateProjectFilesService (RF05, RF09)
    │   ├── search_platform_models_service.py        # SearchPlatformModelsService (RF07)
    │   ├── create_platform_model_service.py         # CreatePlatformModelService (RF08)
    │   ├── update_platform_model_service.py         # UpdatePlatformModelService (RF05, RF08)
    │   ├── link_platform_model_service.py           # LinkPlatformModelService (RF07)
    │   ├── unlink_platform_model_service.py         # UnlinkPlatformModelService (RF07)
    │   ├── list_languages_service.py                # ListLanguagesService (RF08)
    │   └── build_project_service.py                 # BuildProjectService (RF10)
    ├── routes/                                      # Camada 5: Rotas HTTP Flask e Middleware
    │   ├── auth_middleware.py                       # make_auth_required
    │   ├── auth_routes.py                           # create_auth_routes (/api/auth)
    │   ├── project_routes.py                        # create_project_routes (/api/projects)
    │   ├── marketplace_routes.py                    # create_marketplace_routes (/api/marketplace)
    │   └── language_routes.py                       # create_language_routes (/api/linguagens)
    └── infrastructure/                              # Camada 6: Implementações concretas externas
        ├── postgres_connection.py                   # get_connection + ensure_schema
        ├── postgres_query_helper.py                 # run_query
        ├── postgres_user_repository_adapter.py      # PostgresUserRepositoryAdapter(IUserRepository)
        ├── postgres_project_repository_adapter.py   # PostgresProjectRepositoryAdapter(IProjectRepository)
        ├── postgres_platform_model_repository_adapter.py # PostgresPlatformModelRepositoryAdapter(IPlatformModelRepository)
        ├── postgres_language_repository_adapter.py  # PostgresLanguageRepositoryAdapter(ILanguageRepository)
        ├── werkzeug_password_hasher_service.py      # WerkzeugPasswordHasherService(IPasswordHasher)
        ├── jwt_token_service.py                     # JwtTokenService(ITokenService)
        └── java_code_generator_service.py           # JavaCodeGeneratorService(ICodeGeneratorService)
```
