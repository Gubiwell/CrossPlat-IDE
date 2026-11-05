"""
CAMADA 4 - INFRAESTRUTURA: JwtTokenService
Implementa a porta TokenServicePort do domínio usando a biblioteca externa PyJWT.
"""
from datetime import datetime, timedelta, timezone
import jwt
from src.domain.user_entity import User
from src.domain.token_service_port import TokenServicePort


class JwtTokenService(TokenServicePort):
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

