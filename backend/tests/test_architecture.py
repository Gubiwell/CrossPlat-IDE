"""
Garante a REGRA DA DEPENDÊNCIA da Onion Architecture: cada camada só pode
importar das camadas mais internas. Se alguém violar, o teste falha.

Ordem (dentro -> fora): models -> schemas -> repositories -> services -> routes -> infrastructure
"""
import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"

PODE_IMPORTAR = {
    "models": set(),
    "schemas": {"models"},
    "repositories": {"models"},
    "services": {"models", "schemas", "repositories"},
    "routes": {"schemas", "services"},
    "infrastructure": {"models", "schemas", "repositories", "services"},
}
# Bibliotecas externas proibidas nas camadas internas (núcleo da aplicação)
PROIBIDAS = {"flask", "psycopg2", "jwt", "werkzeug", "requests", "subprocess"}
CAMADAS_INTERNAS = ["models", "schemas", "repositories", "services"]


def imports_de(arquivo: Path):
    for no in ast.walk(ast.parse(arquivo.read_text(encoding="utf-8"))):
        if isinstance(no, ast.ImportFrom) and no.module:
            yield no.module
        elif isinstance(no, ast.Import):
            for alias in no.names:
                yield alias.name


@pytest.mark.parametrize("camada", list(PODE_IMPORTAR))
def test_camada_so_importa_de_camadas_internas(camada):
    for arquivo in sorted((SRC / camada).glob("*.py")):
        for modulo in imports_de(arquivo):
            partes = modulo.split(".")
            if partes[0] == "src" and len(partes) > 1 and partes[1] != camada:
                assert partes[1] in PODE_IMPORTAR[camada], (
                    f"{camada}/{arquivo.name} importa '{modulo}', "
                    f"mas '{camada}' só pode importar de {sorted(PODE_IMPORTAR[camada])}"
                )


@pytest.mark.parametrize("camada", CAMADAS_INTERNAS)
def test_nucleo_nao_usa_frameworks_nem_bibliotecas_externas(camada):
    for arquivo in sorted((SRC / camada).glob("*.py")):
        for modulo in imports_de(arquivo):
            assert modulo.split(".")[0] not in PROIBIDAS, (
                f"{camada}/{arquivo.name} importa '{modulo}' (proibido no núcleo)"
            )
