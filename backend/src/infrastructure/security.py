"""
CAMADA 4 - INFRAESTRUTURA: Implementações de segurança
Implementam as interfaces PasswordHasher e TokenService do domínio
usando bibliotecas externas (Werkzeug e PyJWT).
"""
from datetime import datetime, timedelta, timezone
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from src.domain.entities import User
from src.domain.interfaces import PasswordHasher, TokenService


class WerkzeugPasswordHasher(PasswordHasher):
    def hash(self, password: str) -> str:
        return generate_password_hash(password)

    def verify(self, password: str, hashed: str) -> bool:
        return check_password_hash(hashed, password)


class JwtTokenService(TokenService):
    def __init__(self, secret: str, expires_hours: int = 24):
        self.secret = secret
        self.expires_hours = expires_hours

    def generate(self, user: User) -> str:
        payload = {
            "sub": str(user.id),
            "nome": user.nome,
            "exp": datetime.now(timezone.utc) + timedelta(hours=self.expires_hours),
        }
        return jwt.encode(payload, self.secret, algorithm="HS256")

    def decode(self, token: str) -> int:
        try:
            return int(jwt.decode(token, self.secret, algorithms=["HS256"])["sub"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Sessão expirada. Faça login novamente.")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido.")
