"""
CAMADA 2 - CASOS DE USO: AuthenticateUserService
Depende APENAS do domínio (entidades + portas). Recebe as implementações
concretas por injeção de dependência no construtor (ver app.py).
"""
from src.domain.user_repository_port import UserRepositoryPort
from src.domain.password_hasher_port import PasswordHasherPort
from src.domain.token_service_port import TokenServicePort


class AuthenticateUserService:
    """RF02 - Login com geração de token JWT."""

    def __init__(self, users: UserRepositoryPort, hasher: PasswordHasherPort, tokens: TokenServicePort):
        self.users = users
        self.hasher = hasher
        self.tokens = tokens

    def execute(self, email: str, senha: str) -> dict:
        user = self.users.find_by_email((email or "").strip().lower())

        if not user or not self.hasher.verify(senha or "", user.senha):
            raise PermissionError("E-mail ou senha inválidos.")

        return {"token": self.tokens.generate(user), "user": user.to_dict()}

