"""
CAMADA 4 - SERVICES: RegisterUserService
Depende APENAS das camadas internas (models, schemas, repositories e interfaces de services).
Recebe as implementações concretas por injeção de dependência no construtor (ver app.py).
"""
from src.models.user import User
from src.schemas.register_user_schema import RegisterUserSchema
from src.schemas.user_response_schema import UserResponseSchema
from src.repositories.i_user_repository import IUserRepository
from src.services.i_password_hasher import IPasswordHasher


class RegisterUserService:
    """RF01 - Cadastro de usuário."""

    def __init__(self, users: IUserRepository, hasher: IPasswordHasher):
        self.users = users
        self.hasher = hasher

    def execute(self, schema: RegisterUserSchema) -> UserResponseSchema:
        user = User(
            id=None,
            nome=(schema.nome or "").strip(),
            email=(schema.email or "").strip().lower(),
            senha=schema.senha or "",
        )
        user.validate()

        if self.users.find_by_email(user.email):
            raise ValueError("Este e-mail já está cadastrado.")

        user.senha = self.hasher.hash(user.senha)
        return UserResponseSchema.from_model(self.users.create(user))
