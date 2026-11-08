"""
CAMADA 4 - SERVICES: AuthenticateUserService
Depende APENAS das camadas internas (models, schemas, repositories e interfaces de services).
Recebe as implementações concretas por injeção de dependência no construtor (ver app.py).
"""
from src.schemas.login_schema import LoginSchema
from src.schemas.user_response_schema import UserResponseSchema
from src.schemas.auth_response_schema import AuthResponseSchema
from src.repositories.i_user_repository import IUserRepository
from src.services.i_password_hasher import IPasswordHasher
from src.services.i_token_service import ITokenService


class AuthenticateUserService:
    """RF02 - Login com geração de token JWT."""

    def __init__(self, users: IUserRepository, hasher: IPasswordHasher, tokens: ITokenService):
        self.users = users
        self.hasher = hasher
        self.tokens = tokens

    def execute(self, schema: LoginSchema) -> AuthResponseSchema:
        user = self.users.find_by_email((schema.email or "").strip().lower())

        if not user or not self.hasher.verify(schema.senha or "", user.senha):
            raise PermissionError("E-mail ou senha inválidos.")

        return AuthResponseSchema(
            token=self.tokens.generate(user),
            user=UserResponseSchema.from_model(user),
        )
