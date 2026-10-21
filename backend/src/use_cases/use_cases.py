"""
CAMADA 2 - CASOS DE USO
Um caso de uso por ação do sistema (RF01 a RF04).
Depende APENAS do domínio (entidades + interfaces). Recebe as implementações
concretas por injeção de dependência no construtor (ver app.py).
"""
from src.domain.entities import User, Project
from src.domain.interfaces import UserRepository, ProjectRepository, PasswordHasher, TokenService


class RegisterUserUseCase:
    """RF01 - Cadastro de usuário."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher):
        self.users = users
        self.hasher = hasher

    def execute(self, nome: str, email: str, senha: str) -> dict:
        user = User(id=None, nome=(nome or "").strip(), email=(email or "").strip().lower(), senha=senha or "")
        user.validate()

        if self.users.find_by_email(user.email):
            raise ValueError("Este e-mail já está cadastrado.")

        user.senha = self.hasher.hash(user.senha)
        return self.users.create(user).to_dict()


class AuthenticateUserUseCase:
    """RF02 - Login com geração de token JWT."""

    def __init__(self, users: UserRepository, hasher: PasswordHasher, tokens: TokenService):
        self.users = users
        self.hasher = hasher
        self.tokens = tokens

    def execute(self, email: str, senha: str) -> dict:
        user = self.users.find_by_email((email or "").strip().lower())

        if not user or not self.hasher.verify(senha or "", user.senha):
            raise PermissionError("E-mail ou senha inválidos.")

        return {"token": self.tokens.generate(user), "user": user.to_dict()}


class CreateProjectUseCase:
    """RF03 - Criar projeto (por enquanto, apenas nome)."""

    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(self, nome: str, usuario_id: int) -> dict:
        project = Project(id=None, nome=(nome or "").strip(), usuario_id=usuario_id)
        project.validate()
        return self.projects.create(project).to_dict()


class ListProjectsUseCase:
    """RF04 - Listar projetos do usuário."""

    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(self, usuario_id: int) -> list:
        return [p.to_dict() for p in self.projects.list_by_user(usuario_id)]


class DeleteProjectUseCase:
    """RF04 - Excluir projeto do usuário."""

    def __init__(self, projects: ProjectRepository):
        self.projects = projects

    def execute(self, project_id: int, usuario_id: int) -> None:
        # Só apaga se o projeto pertencer ao usuário
        if not self.projects.delete(project_id, usuario_id):
            raise LookupError("Projeto não encontrado.")
