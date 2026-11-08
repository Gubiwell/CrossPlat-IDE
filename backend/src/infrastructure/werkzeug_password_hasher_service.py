"""
CAMADA 4 - INFRAESTRUTURA: WerkzeugPasswordHasherService
Implementa a porta PasswordHasherPort do domínio usando a biblioteca externa Werkzeug.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from src.domain.password_hasher_port import PasswordHasherPort


class WerkzeugPasswordHasherService(PasswordHasherPort):
    def hash(self, password: str) -> str:
        return generate_password_hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return check_password_hash(hashed, password)

