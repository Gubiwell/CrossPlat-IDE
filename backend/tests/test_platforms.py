"""RF07 e RF08: marketplace de plataformas e template protegido."""
import pytest

from src.models.project import Project
from src.schemas.create_platform_model_schema import CreatePlatformModelSchema
from src.schemas.link_platform_model_schema import LinkPlatformModelSchema
from src.schemas.update_platform_model_schema import UpdatePlatformModelSchema
from src.services.create_platform_model_service import CreatePlatformModelService
from src.services.link_platform_model_service import LinkPlatformModelService
from src.services.search_platform_models_service import SearchPlatformModelsService
from src.services.unlink_platform_model_service import UnlinkPlatformModelService
from src.services.update_platform_model_service import UpdatePlatformModelService

ANA, BIA = 1, 2


def criar_plataforma(platforms, languages, nome="Arduino", codigo=None, linguagem="C++", criador=ANA):
    return CreatePlatformModelService(platforms, languages).execute(
        CreatePlatformModelSchema(nome=nome, codigo=codigo, linguagem=linguagem), criador
    )


def novo_projeto(projects, dono=ANA):
    return projects.create(Project(id=None, nome="P", usuario_id=dono))


# ---------- criar (RF08) ----------
def test_criar_gera_template_com_cabecalho_protegido(platforms, languages):
    m = criar_plataforma(platforms, languages)
    codigo = platforms.items[m.id].codigo
    assert codigo.startswith("platform Arduino: C++ {")
    assert codigo.endswith("}")


def test_criar_sem_nome_e_rejeitado(platforms, languages):
    with pytest.raises(ValueError, match="nome"):
        criar_plataforma(platforms, languages, nome="  ")


def test_criar_com_nome_repetido_e_rejeitado(platforms, languages):
    criar_plataforma(platforms, languages)
    with pytest.raises(ValueError, match="Já existe"):
        criar_plataforma(platforms, languages)


def test_criar_sem_codigo_e_sem_linguagem_e_rejeitado(platforms, languages):
    with pytest.raises(ValueError, match="linguagem"):
        criar_plataforma(platforms, languages, linguagem=None)


def test_linguagem_e_deduzida_do_codigo_enviado(platforms, languages):
    m = criar_plataforma(platforms, languages, nome="Unity", codigo="platform Unity: C# {\n}", linguagem=None)
    assert platforms.items[m.id].linguagem_nome == "C#"
    assert platforms.items[m.id].linguagem_id == 2


def test_codigo_fora_da_estrutura_protegida_e_rejeitado(platforms, languages):
    with pytest.raises(ValueError, match="estrutura protegida"):
        criar_plataforma(platforms, languages, nome="X", codigo="qualquer coisa", linguagem="C++")


# ---------- editar (RF05/RF08) ----------
def test_criador_pode_editar_o_corpo_do_template(platforms, languages):
    m = criar_plataforma(platforms, languages)
    novo = "platform Arduino: C++ {\n  trigger x\n}"
    UpdatePlatformModelService(platforms).execute(m.id, ANA, UpdatePlatformModelSchema(novo))
    assert platforms.items[m.id].codigo == novo


def test_so_o_criador_pode_editar(platforms, languages):
    m = criar_plataforma(platforms, languages)
    with pytest.raises(PermissionError):
        UpdatePlatformModelService(platforms).execute(m.id, BIA, UpdatePlatformModelSchema("platform Arduino: C++ {}"))


def test_editar_plataforma_inexistente(platforms):
    with pytest.raises(LookupError):
        UpdatePlatformModelService(platforms).execute(99, ANA, UpdatePlatformModelSchema("x"))


@pytest.mark.parametrize(
    "novo_codigo",
    [
        "platform Outra: C++ {\n}",    # cabeçalho alterado
        "platform Arduino: C# {\n}",   # linguagem alterada
        "platform Arduino: C++ {\n x", # sem o '}' final
        "",                            # vazio
    ],
)
def test_nao_permite_alterar_secoes_protegidas(platforms, languages, novo_codigo):
    m = criar_plataforma(platforms, languages)
    original = platforms.items[m.id].codigo
    with pytest.raises(ValueError):
        UpdatePlatformModelService(platforms).execute(m.id, ANA, UpdatePlatformModelSchema(novo_codigo))
    assert platforms.items[m.id].codigo == original  # nada foi gravado


# ---------- vincular / desvincular (RF07) ----------
def test_vincular_plataforma_ao_projeto(projects, platforms, languages):
    p, m = novo_projeto(projects), criar_plataforma(platforms, languages)
    LinkPlatformModelService(projects, platforms).execute(p.id, ANA, LinkPlatformModelSchema(m.id))
    assert [x.id for x in platforms.list_by_project(p.id)] == [m.id]


def test_vincular_em_projeto_de_outro_usuario_e_rejeitado(projects, platforms, languages):
    p, m = novo_projeto(projects, dono=ANA), criar_plataforma(platforms, languages)
    with pytest.raises(LookupError, match="Projeto"):
        LinkPlatformModelService(projects, platforms).execute(p.id, BIA, LinkPlatformModelSchema(m.id))


@pytest.mark.parametrize("model_id", [None, 0, 999])
def test_vincular_plataforma_inexistente_e_rejeitado(projects, platforms, model_id):
    p = novo_projeto(projects)
    with pytest.raises(LookupError, match="Plataforma"):
        LinkPlatformModelService(projects, platforms).execute(p.id, ANA, LinkPlatformModelSchema(model_id))


def test_desvincular_remove_apenas_o_vinculo_e_nao_a_plataforma(projects, platforms, languages):
    p, m = novo_projeto(projects), criar_plataforma(platforms, languages)
    LinkPlatformModelService(projects, platforms).execute(p.id, ANA, LinkPlatformModelSchema(m.id))
    UnlinkPlatformModelService(projects, platforms).execute(p.id, m.id, ANA)
    assert platforms.list_by_project(p.id) == []
    assert platforms.find_by_id(m.id) is not None  # continua no marketplace


def test_desvincular_plataforma_nao_vinculada_e_rejeitado(projects, platforms, languages):
    p, m = novo_projeto(projects), criar_plataforma(platforms, languages)
    with pytest.raises(LookupError, match="não vinculada"):
        UnlinkPlatformModelService(projects, platforms).execute(p.id, m.id, ANA)


def test_desvincular_em_projeto_alheio_e_rejeitado(projects, platforms, languages):
    p, m = novo_projeto(projects, dono=ANA), criar_plataforma(platforms, languages)
    with pytest.raises(LookupError, match="Projeto"):
        UnlinkPlatformModelService(projects, platforms).execute(p.id, m.id, BIA)


# ---------- buscar (RF07) ----------
def test_busca_filtra_por_nome_e_vazio_lista_todas(platforms, languages):
    criar_plataforma(platforms, languages, nome="Arduino")
    criar_plataforma(platforms, languages, nome="Unity", linguagem="C#")
    svc = SearchPlatformModelsService(platforms)
    assert [m.nome for m in svc.execute("ardu")] == ["Arduino"]
    assert len(svc.execute("")) == 2
    assert len(svc.execute(None)) == 2
