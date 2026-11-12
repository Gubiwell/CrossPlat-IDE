"""
Testes das regras de negócio (RF01 a RF10).

Os services dependem apenas de INTERFACES (repositories/ e services/i_*.py).
Por isso os testes usam repositórios FALSOS em memória: não precisam de
PostgreSQL, Flask, Docker nem do generator.jar, e rodam em milissegundos.
Isso só é possível por causa da Clean/Onion Architecture.
"""
from datetime import datetime

import pytest

from src.models.generated_file import GeneratedFile
from src.models.language import Language
from src.repositories.i_language_repository import ILanguageRepository
from src.repositories.i_platform_model_repository import IPlatformModelRepository
from src.repositories.i_project_repository import IProjectRepository
from src.repositories.i_user_repository import IUserRepository
from src.services.i_code_generator_service import ICodeGeneratorService
from src.services.i_password_hasher import IPasswordHasher
from src.services.i_token_service import ITokenService


class FakeUserRepository(IUserRepository):
    def __init__(self):
        self.by_email = {}

    def create(self, user):
        user.id = len(self.by_email) + 1
        user.data_criacao = datetime.now()
        self.by_email[user.email] = user
        return user

    def find_by_email(self, email):
        return self.by_email.get(email)


class FakeProjectRepository(IProjectRepository):
    def __init__(self):
        self.items = {}
        self._next = 1

    def create(self, project):
        project.id = self._next
        self._next += 1
        project.data_criacao = datetime.now()
        self.items[project.id] = project
        return project

    def list_by_user(self, usuario_id):
        return [p for p in self.items.values() if p.usuario_id == usuario_id]

    def find_by_id(self, project_id, usuario_id):
        p = self.items.get(project_id)
        return p if p and p.usuario_id == usuario_id else None

    def update_files(self, project):
        self.items[project.id] = project
        return True

    def delete(self, project_id, usuario_id):
        if self.find_by_id(project_id, usuario_id):
            del self.items[project_id]
            return True
        return False


class FakePlatformModelRepository(IPlatformModelRepository):
    def __init__(self):
        self.items = {}
        self.links = set()  # (project_id, model_id)

    def create(self, model):
        model.id = len(self.items) + 1
        model.data_criacao = datetime.now()
        self.items[model.id] = model
        return model

    def find_by_id(self, model_id):
        return self.items.get(model_id)

    def find_by_name(self, nome):
        return next((m for m in self.items.values() if m.nome.lower() == nome.lower()), None)

    def search(self, query):
        return [m for m in self.items.values() if query.lower() in m.nome.lower()]

    def update_code(self, model_id, codigo):
        self.items[model_id].codigo = codigo
        return True

    def list_by_project(self, project_id):
        return [self.items[m] for (p, m) in sorted(self.links) if p == project_id]

    def link_to_project(self, project_id, model_id):
        self.links.add((project_id, model_id))

    def unlink_from_project(self, project_id, model_id):
        if (project_id, model_id) in self.links:
            self.links.discard((project_id, model_id))
            return True
        return False


class FakeLanguageRepository(ILanguageRepository):
    def __init__(self):
        self.items = [Language(id=1, nome="C++"), Language(id=2, nome="C#")]

    def list_all(self):
        return list(self.items)

    def find_by_name(self, nome):
        return next((l for l in self.items if l.nome.lower() == nome.lower()), None)


class FakePasswordHasher(IPasswordHasher):
    def hash(self, password):
        return "hash::" + password

    def verify(self, password, hashed):
        return hashed == "hash::" + password


class FakeTokenService(ITokenService):
    def generate(self, user):
        return f"token-{user.id}"

    def decode(self, token):
        return int(token.split("-")[1])


class FakeCodeGenerator(ICodeGeneratorService):
    """Registra com quais dados o gerador foi chamado, sem rodar o JAR."""

    def __init__(self):
        self.calls = []

    def generate(self, project, platform_models):
        self.calls.append((project, list(platform_models)))
        return [GeneratedFile(nome="Main.cpp", conteudo="// gerado")], "log ok"


@pytest.fixture
def users():
    return FakeUserRepository()


@pytest.fixture
def projects():
    return FakeProjectRepository()


@pytest.fixture
def platforms():
    return FakePlatformModelRepository()


@pytest.fixture
def languages():
    return FakeLanguageRepository()


@pytest.fixture
def hasher():
    return FakePasswordHasher()


@pytest.fixture
def tokens():
    return FakeTokenService()


@pytest.fixture
def generator():
    return FakeCodeGenerator()
