"""
CAMADA 6 - INFRASTRUCTURE: JavaCodeGeneratorService (RF10 / RNF03 / RNF05)
Implementa a interface ICodeGeneratorService invocando o generator.jar em diretório isolado.
Baseado fielmente na referência build.py.
"""
import os
import shutil
import subprocess
from typing import List, Tuple
from src.models.project import Project
from src.models.platform_model import PlatformModel
from src.models.generated_file import GeneratedFile
from src.services.i_code_generator_service import ICodeGeneratorService


class JavaCodeGeneratorService(ICodeGeneratorService):
    def __init__(self, jar_path: str, temp_build_dir: str):
        self.jar_path = jar_path
        self.temp_build_dir = temp_build_dir

    def generate(
        self, project: Project, modelos: List[PlatformModel]
    ) -> Tuple[List[GeneratedFile], str]:
        if not os.path.isfile(self.jar_path):
            raise RuntimeError(
                f"Arquivo do gerador não encontrado em '{self.jar_path}'. "
                "Adicione o arquivo generator.jar na pasta generator/."
            )

        # 1. Preparar pasta temporária única e isolada para este build (RNF05)
        build_path = os.path.join(self.temp_build_dir, str(project.id))
        output_path = os.path.join(build_path, "saida")

        if os.path.exists(build_path):
            shutil.rmtree(build_path)
        os.makedirs(output_path, exist_ok=True)

        # 2. Concatenação do GPL (Deploy + GPL + Plataformas vinculadas)
        full_gpl = project.deploy_model or ""
        full_gpl += "\n\n" + (project.gpl_code or "")
        for modelo in modelos:
            full_gpl += "\n\n" + (modelo.codigo or "")

        # 3. Escrita dos arquivos físicos (.crossplat)
        with open(os.path.join(build_path, "gpl.crossplat"), "w", encoding="utf-8") as f:
            f.write(full_gpl)
        with open(os.path.join(build_path, "datatype.crossplat"), "w", encoding="utf-8") as f:
            f.write(project.datatype_def or "")
        with open(os.path.join(build_path, "global.crossplat"), "w", encoding="utf-8") as f:
            f.write(project.global_functions or "")

        # 4. Execução do JAR via linha de comando (RNF03)
        cmd = [
            "java",
            "-jar",
            self.jar_path,
            "datatype.crossplat",
            "global.crossplat",
            "gpl.crossplat",
            "-o",
            "saida",
        ]
        resultado = subprocess.run(
            cmd,
            cwd=build_path,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if resultado.returncode != 0:
            detalhes = (resultado.stderr or resultado.stdout or "").strip()
            raise RuntimeError(detalhes or "Falha ao executar o compilador Xtext (.jar).")

        # 5. Coleta dos arquivos gerados na pasta saida/
        arquivos_gerados: List[GeneratedFile] = []
        for root_dir, _, filenames in os.walk(output_path):
            for filename in sorted(filenames):
                f_path = os.path.join(root_dir, filename)
                rel_name = os.path.relpath(f_path, output_path).replace("\\", "/")
                with open(f_path, "r", encoding="utf-8", errors="replace") as f:
                    arquivos_gerados.append(GeneratedFile(nome=rel_name, conteudo=f.read()))

        return arquivos_gerados, resultado.stdout or ""
