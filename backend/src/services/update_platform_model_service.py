"""
CAMADA 4 - SERVICES: UpdatePlatformModelService
Depende APENAS das camadas internas (schemas e repositories).
"""
import re
from src.schemas.update_platform_model_schema import UpdatePlatformModelSchema
from src.schemas.platform_model_response_schema import PlatformModelResponseSchema
from src.repositories.i_platform_model_repository import IPlatformModelRepository


class UpdatePlatformModelService:
    """RF05 / RF08 - Salvar código de modelo de plataforma preservando cabeçalho protegido."""

    def __init__(self, platform_models: IPlatformModelRepository):
        self.platform_models = platform_models

    def execute(
        self, model_id: int, usuario_id: int, schema: UpdatePlatformModelSchema
    ) -> PlatformModelResponseSchema:
        model = self.platform_models.find_by_id(model_id)
        if not model:
            raise LookupError("Plataforma não encontrada.")
        if model.criador_id != usuario_id:
            raise PermissionError("Apenas o criador pode editar esta plataforma.")

        # Extrai o cabeçalho original protegido (ex: "platform Arduino: C++ {")
        header_match = re.match(r"^(platform\s+\S+\s*:\s*\S+\s*\{)", model.codigo.strip())
        novo_codigo = (schema.codigo or "").strip()

        if header_match:
            header_original = header_match.group(1)
            if not novo_codigo.startswith(header_original) or not novo_codigo.endswith("}"):
                raise ValueError(
                    f"As seções fora das chaves são protegidas. Mantenha o cabeçalho '{header_original}' e o '}}' final."
                )

        model.codigo = novo_codigo
        model.validate()
        self.platform_models.update_code(model_id, model.codigo)
        return PlatformModelResponseSchema.from_model(model)
