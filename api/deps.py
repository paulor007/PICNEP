"""
Dependências compartilhadas entre rotas.

get_db: injeção de sessão do banco
get_current_user: verifica JWT e retorna usuário autenticado
require_role: verifica se usuário tem permissão suficiente
"""

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import decode_access_token
from models.user import User

# Define onde o FastAPI espera o token (header Authorization: Bearer <token>)
# tokenUrl é a URL do login (usada pelo botão Authorize no Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency que verifica JWT e retorna o usuário autenticado.

    Como funciona:
    1. FastAPI extrai o token do header Authorization
    2. decode_access_token verifica assinatura e expiração
    3. Busca usuário no banco pelo email do token
    4. Se tudo OK, retorna o User
    5. Se qualquer passo falhar → 401

    Uso nos endpoints:
      @router.get("/protegido")
      def rota(user: User = Depends(get_current_user)):
          return {"msg": f"Olá {user.name}"}
    """
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Token sem identificação")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Conta desativada")

    return user


def require_role(*allowed_roles: str):
    """
    Factory de dependency que verifica role do usuário.

    Uso:
      @router.get("/admin-only")
      def rota(user: User = Depends(require_role("admin"))):
          return {"msg": "Só admin vê isso"}

      @router.get("/gestores")
      def rota(user: User = Depends(require_role("admin", "gestor"))):
          return {"msg": "Admin e gestor veem isso"}
    """
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Acesso negado. Requer perfil: {', '.join(allowed_roles)}"
            )
        return user
    return role_checker


__all__ = ["get_db", "get_current_user", "require_role", "oauth2_scheme"]