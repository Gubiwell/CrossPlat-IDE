"""
CAMADA 6 - INFRASTRUCTURE: WerkzeugPasswordHasherService
Implementa a interface IPasswordHasher usando a biblioteca externa Werkzeug.
"""
from werkzeug.security import generate_password_hash, check_password_hash
from src.services.i_password_hasher import IPasswordHasher


class WerkzeugPasswordHasherService(IPasswordHasher):
    def hash(self, password: str) -> str:
        return generate_password_hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return check_password_hash(hashed, password)
