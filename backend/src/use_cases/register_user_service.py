"""
CAMADA 2 - CASOS DE USO: RegisterUserService
Depende APENAS do domínio (entidades + portas). Recebe as implementações
concretas por injeção de dependência no construtor (ver app.py).
"""
from src.domain.user_entity import User
from src.domain.user_repository_port import UserRepositoryPort
from src.domain.password_hasher_port import PasswordHasherPort


class RegisterUserService:
    """RF01 - Cadastro de usuário."""

    def __init__(self, users: UserRepositoryPort, hasher: PasswordHasherPort):
        self.users = users
        self.hasher = hasher

    def execute(self, nome: str, email: str, senha: str) -> dict:
        user = User(id=None, nome=(nome or "").strip(), email=(email or "").strip().lower(), senha=senha or "")
        user.validate()

        if self.users.find_by_email(user.email):
            raise ValueError("Este e-mail já está cadastrado.")

        user.senha = self.hasher.hash(user.senha)
        return self.users.create(user).to_dict()

