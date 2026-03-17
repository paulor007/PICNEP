"""
Endpoints de autenticação: registro e login.

Imports:
- OAuth2PasswordBearer: define onde o FastAPI espera o token.
  Configura o botão "Authorize" no Swagger automaticamente.

Fluxo de registro:
  1. Usuário manda name + email + password
  2. API verifica se email já existe
  3. Faz hash da senha (bcrypt)
  4. Salva no banco (NUNCA salva senha em texto puro)
  5. Retorna dados do usuário (sem senha)

Fluxo de login:
  1. Usuário manda email + password
  2. API busca usuário pelo email
  3. Compara senha com hash (bcrypt verify)
  4. Se OK, gera token JWT com email e role
  5. Retorna token
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db
from models.user import User
from schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from core.security import hash_password, verify_password, creat_access_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """
    Cria nova conta de usuário.

    Validações:
    - Email não pode já existir no banco
    - Role deve ser admin, gestor ou analista
    - Senha é transformada em hash antes de salvar
    """
    # Verificar se email já existe
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email já cadastrado"
        )
    
    # Validar role
    valid_roles = {"admin", "gestor", "analista"}
    if data.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Role inválido. Use: {', '.join(valid_roles)}"
        )
    
    # Criar usuário com senha hasheada
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),  # NUNCA salvar texto puro
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Faz login e retorna token JWT.

    O token contém:
    - sub: email do usuário (subject)
    - role: perfil de acesso
    - exp: data/hora de expiração

    O frontend guarda esse token e manda em toda requisição:
    Authorization: Bearer <token>
    """
    # Buscar usuário
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Email ou senha incorretos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Conta desativada. Contate o administrador."
        )
    
    # Gerar token
    token = creat_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return TokenResponse(
        access_token=token,
        role=user.role,
        name=user.name,
    )