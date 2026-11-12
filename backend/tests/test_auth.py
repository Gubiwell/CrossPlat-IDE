"""RF01 (cadastro) e RF02 (login)."""
import pytest

from src.models.user import User
from src.schemas.login_schema import LoginSchema
from src.schemas.register_user_schema import RegisterUserSchema
from src.services.authenticate_user_service import AuthenticateUserService
from src.services.register_user_service import RegisterUserService


def cadastrar(users, hasher, nome="Ana", email="ana@x.com", senha="123456"):
    return RegisterUserService(users, hasher).execute(RegisterUserSchema(nome, email, senha))


def test_cadastro_valido_retorna_usuario_sem_senha(users, hasher):
    r = cadastrar(users, hasher).to_dict()
    assert r["email"] == "ana@x.com"
    assert "senha" not in r


def test_senha_e_guardada_com_hash_nunca_em_texto(users, hasher):
    cadastrar(users, hasher, senha="123456")
    assert users.by_email["ana@x.com"].senha != "123456"
    assert users.by_email["ana@x.com"].senha == hasher.hash("123456")


def test_email_e_normalizado_para_minusculo_e_sem_espacos(users, hasher):
    cadastrar(users, hasher, email="  ANA@X.com ")
    assert "ana@x.com" in users.by_email


def test_email_duplicado_e_rejeitado(users, hasher):
    cadastrar(users, hasher)
    with pytest.raises(ValueError, match="já está cadastrado"):
        cadastrar(users, hasher, nome="Outra", email="ANA@x.com")


@pytest.mark.parametrize(
    "nome,email,senha,trecho",
    [
        ("A", "a@x.com", "123456", "nome"),       # nome com menos de 2 caracteres
        ("", "a@x.com", "123456", "nome"),
        ("Ana", "sem-arroba", "123456", "E-mail"),
        ("Ana", "", "123456", "E-mail"),
        ("Ana", "a@x.com", "12345", "senha"),      # senha com menos de 6 caracteres
        ("Ana", "a@x.com", "", "senha"),
    ],
)
def test_cadastro_invalido_e_rejeitado(users, hasher, nome, email, senha, trecho):
    with pytest.raises(ValueError, match=trecho):
        cadastrar(users, hasher, nome, email, senha)


@pytest.mark.parametrize("nome,senha", [("Al", "123456")])
def test_limites_minimos_sao_aceitos(users, hasher, nome, senha):
    assert cadastrar(users, hasher, nome=nome, senha=senha).nome == "Al"


def test_login_correto_retorna_token_e_usuario_sem_senha(users, hasher, tokens):
    cadastrar(users, hasher)
    r = AuthenticateUserService(users, hasher, tokens).execute(LoginSchema("ana@x.com", "123456")).to_dict()
    assert r["token"] == "token-1"
    assert "senha" not in r["user"]


def test_login_aceita_email_com_maiusculas(users, hasher, tokens):
    cadastrar(users, hasher)
    r = AuthenticateUserService(users, hasher, tokens).execute(LoginSchema(" ANA@x.com ", "123456"))
    assert r.token


def test_login_senha_errada_e_email_inexistente_dao_a_mesma_mensagem(users, hasher, tokens):
    """Não revelar se o e-mail existe (evita enumeração de usuários)."""
    cadastrar(users, hasher)
    svc = AuthenticateUserService(users, hasher, tokens)
    with pytest.raises(PermissionError) as senha_errada:
        svc.execute(LoginSchema("ana@x.com", "errada"))
    with pytest.raises(PermissionError) as sem_usuario:
        svc.execute(LoginSchema("ninguem@x.com", "123456"))
    assert str(senha_errada.value) == str(sem_usuario.value)


@pytest.mark.parametrize(
    "nome,email,senha,ok",
    [("Ab", "a@b", "123456", True), ("A", "a@b", "123456", False), ("Ab", "ab", "123456", False), ("Ab", "a@b", "12345", False)],
)
def test_user_validate_limites(nome, email, senha, ok):
    user = User(id=None, nome=nome, email=email, senha=senha)
    if ok:
        user.validate()
    else:
        with pytest.raises(ValueError):
            user.validate()
