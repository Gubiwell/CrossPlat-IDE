"""RF03 a RF06 e RF10: projetos, isolamento por usuário e build."""
import pytest

from src.models.platform_model import PlatformModel
from src.schemas.create_project_schema import CreateProjectSchema
from src.schemas.update_project_schema import UpdateProjectSchema
from src.services.build_project_service import BuildProjectService
from src.services.create_project_service import CreateProjectService
from src.services.delete_project_service import DeleteProjectService
from src.services.get_project_detail_service import GetProjectDetailService
from src.services.list_projects_service import ListProjectsService
from src.services.update_project_files_service import UpdateProjectFilesService

ANA, BIA = 1, 2


def criar(projects, usuario_id, nome="P1"):
    return CreateProjectService(projects).execute(CreateProjectSchema(nome), usuario_id)


def test_criar_projeto_remove_espacos_do_nome(projects):
    assert criar(projects, ANA, "  Meu app  ").nome == "Meu app"


@pytest.mark.parametrize("nome", ["", "   ", None])
def test_criar_projeto_sem_nome_e_rejeitado(projects, nome):
    with pytest.raises(ValueError, match="obrigatório"):
        criar(projects, ANA, nome)


def test_listar_mostra_apenas_projetos_do_proprio_usuario(projects):
    criar(projects, ANA, "da Ana")
    criar(projects, BIA, "da Bia")
    nomes = [p.nome for p in ListProjectsService(projects).execute(ANA)]
    assert nomes == ["da Ana"]


def test_excluir_projeto_proprio(projects):
    p = criar(projects, ANA)
    DeleteProjectService(projects).execute(p.id, ANA)
    assert ListProjectsService(projects).execute(ANA) == []


def test_nao_e_possivel_excluir_projeto_de_outro_usuario(projects):
    p = criar(projects, ANA)
    with pytest.raises(LookupError):
        DeleteProjectService(projects).execute(p.id, BIA)
    assert len(ListProjectsService(projects).execute(ANA)) == 1  # continua existindo


def test_detalhe_traz_arquivos_e_plataformas_vinculadas(projects, platforms):
    p = criar(projects, ANA)
    m = platforms.create(PlatformModel(None, "Arduino", "platform Arduino: C++ {}", ANA))
    platforms.link_to_project(p.id, m.id)
    detalhe = GetProjectDetailService(projects, platforms).execute(p.id, ANA)
    assert detalhe.id == p.id
    assert len(detalhe.to_dict()["modelos_vinculados"]) == 1


def test_detalhe_de_projeto_alheio_nao_e_encontrado(projects, platforms):
    p = criar(projects, ANA)
    with pytest.raises(LookupError):
        GetProjectDetailService(projects, platforms).execute(p.id, BIA)


def test_salvar_atualiza_apenas_os_arquivos_enviados(projects, platforms):
    p = criar(projects, ANA)
    svc = UpdateProjectFilesService(projects, platforms)
    svc.execute(p.id, ANA, UpdateProjectSchema(gpl_code="class A {}", deploy_model="deploy D {}"))
    svc.execute(p.id, ANA, UpdateProjectSchema(datatype_def="type T"))  # não envia gpl nem deploy
    salvo = projects.items[p.id]
    assert salvo.gpl_code == "class A {}"        # preservado
    assert salvo.deploy_model == "deploy D {}"   # preservado
    assert salvo.datatype_def == "type T"


def test_salvar_aceita_apagar_um_arquivo_com_texto_vazio(projects, platforms):
    p = criar(projects, ANA)
    svc = UpdateProjectFilesService(projects, platforms)
    svc.execute(p.id, ANA, UpdateProjectSchema(gpl_code="algo"))
    svc.execute(p.id, ANA, UpdateProjectSchema(gpl_code=""))
    assert projects.items[p.id].gpl_code == ""


def test_nao_e_possivel_salvar_em_projeto_de_outro_usuario(projects, platforms):
    p = criar(projects, ANA)
    with pytest.raises(LookupError):
        UpdateProjectFilesService(projects, platforms).execute(p.id, BIA, UpdateProjectSchema(gpl_code="hack"))
    assert projects.items[p.id].gpl_code == ""


def test_build_envia_ao_gerador_o_projeto_e_as_plataformas_vinculadas(projects, platforms, generator):
    p = criar(projects, ANA)
    m = platforms.create(PlatformModel(None, "Arduino", "platform Arduino: C++ {}", ANA))
    platforms.link_to_project(p.id, m.id)
    r = BuildProjectService(projects, platforms, generator).execute(p.id, ANA)
    assert r.sucesso is True
    projeto_enviado, modelos_enviados = generator.calls[0]
    assert projeto_enviado.id == p.id
    assert [x.nome for x in modelos_enviados] == ["Arduino"]


def test_build_de_projeto_alheio_nao_chama_o_gerador(projects, platforms, generator):
    p = criar(projects, ANA)
    with pytest.raises(LookupError):
        BuildProjectService(projects, platforms, generator).execute(p.id, BIA)
    assert generator.calls == []
