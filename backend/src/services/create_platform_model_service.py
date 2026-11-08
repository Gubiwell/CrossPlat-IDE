"""
CAMADA 4 - SERVICES: CreatePlatformModelService
Depende APENAS das camadas internas (models, schemas e repositories).
"""
import re
from src.models.platform_model import PlatformModel
from src.schemas.create_platform_model_schema import CreatePlatformModelSchema
from src.schemas.platform_model_response_schema import PlatformModelResponseSchema
from src.repositories.i_platform_model_repository import IPlatformModelRepository
from src.repositories.i_language_repository import ILanguageRepository


class CreatePlatformModelService:
    """RF08 - Criar nova plataforma com template de seções protegidas."""

    def __init__(
        self,
        platform_models: IPlatformModelRepository,
        languages: ILanguageRepository,
    ):
        self.platform_models = platform_models
        self.languages = languages

    def execute(
        self, schema: CreatePlatformModelSchema, criador_id: int
    ) -> PlatformModelResponseSchema:
        nome = (schema.nome or "").strip()
        if not nome:
            raise ValueError("Informe o nome da plataforma.")

        if self.platform_models.find_by_name(nome):
            raise ValueError("Já existe uma plataforma com este nome.")

        linguagem_nome = (schema.linguagem or "").strip()
        codigo = (schema.codigo or "").strip()

        if not linguagem_nome and codigo:
            match = re.match(r"^platform\s+\S+\s*:\s*(\S+)\s*\{", codigo)
            if match:
                linguagem_nome = match.group(1)

        linguagem_id = None
        if linguagem_nome:
            lang = self.languages.find_by_name(linguagem_nome)
            if lang:
                linguagem_id = lang.id
                linguagem_nome = lang.nome

        if not codigo:
            if not linguagem_nome:
                raise ValueError("Selecione uma linguagem.")
            codigo = f"platform {nome}: {linguagem_nome} {{\n\t// Escreva os triggers aqui\n}}"

        model = PlatformModel(
            id=None,
            nome=nome,
            codigo=codigo,
            criador_id=criador_id,
            linguagem_id=linguagem_id,
            linguagem_nome=linguagem_nome,
        )
        model.validate()

        created = self.platform_models.create(model)
        return PlatformModelResponseSchema.from_model(created)
