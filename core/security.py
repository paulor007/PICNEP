"""
Módulo de segurança: hash de senha + geração/verificação de JWT.

Imports:
- passlib.context.CryptContext: gerencia hash de senhas.
  NUNCA guarde senha em texto puro no banco. O bcrypt transforma
  "minhasenha123" em "$2b$12$LJ3m5..." (impossível reverter).
  Para verificar, o bcrypt compara o hash — não a senha original.

- python_jose.jwt: gera e decodifica tokens JWT.
  JWT = JSON Web Token. É uma string que contém dados (email, role, exp)
  assinada com uma chave secreta. Se alguém alterar o conteúdo, a
  assinatura quebra e o token é rejeitado.

- datetime + timedelta: para definir expiração do token.

Por que bcrypt (e não MD5/SHA256)?
- MD5/SHA256 são rápidos demais — um atacante testa bilhões por segundo
- bcrypt é LENTO de propósito — cada tentativa demora ~100ms
- Isso torna ataques de força bruta inviáveis
"""

from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from passlib.context import CryptContext

from core.config import settings

# ── Hash de senha ──
# schemes=["bcrypt"]: usa bcrypt para hash
# deprecated="auto": atualiza hashes antigos automaticamente
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Transforma senha em hash bcrypt (irreversível)."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara senha digitada com hash do banco. Retorna True/False."""
    return pwd_context.verify(plain_password, hashed_password)

# ── JWT ──

def creat_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Gera token JWT com dados e expiração.

    data: {"sub": "email@example.com", "role": "admin"}
    O campo "sub" (subject) é padrão JWT para identificar o usuário.
    O campo "exp" (expiration) é adicionado automaticamente.

    Retorna string tipo: "eyJhbGciOiJIUzI1NiIs..."
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta (
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode["exp"] = expire
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """
    Decodifica token JWT e retorna os dados.

    Se o token for inválido, expirado ou adulterado → retorna None.
    Se válido → retorna dict com "sub" (email) e "role".
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None

