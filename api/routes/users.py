"""
Endpoints de gestão de usuários — só admin acessa.

O admin pode:
- Listar todos os usuários
- Ver detalhes de um usuário
- Criar usuário (definir role)
- Editar role de um usuário
- Desativar/ativar conta
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, require_role
from models.user import User
from schemas.auth import RegisterRequest, UserResponse
from core.security import hash_password

router = APIRouter(prefix="/api/v1/users", tags=["Usuários (Admin)"])

@router.get("/", response_model=list[UserResponse])
def list_user(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """Lista todos os usuários. Apenas admin."""
    return db.query(User).offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")), 
):
    """Detalhes de um usuário."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    data: RegisterRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """Admin cria usuário com role definido."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    valid_roles = {"admin", "gestor", "analista"}
    if data.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role inválido. Use: {', '.join(valid_roles)}")
    
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/role")
def update_role(
    user_id: int,
    role: str = Query(..., description="Novo role: admin, gestor ou analista"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """Admin altera role de um usuário."""
    valid_roles = {"admin", "gestor", "analista"}
    if role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Role inválido. Use: {', '.join(valid_roles)}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user.role = role
    db.commit()
    return {"message": f"Role de {user.name} alterado para {role}"}

@router.put("/{user_id}/toggle-active")
def toggle_active(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """Admin ativa/desativa conta de um usuário."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user.is_active = not user.is_active
    db.commit()

    status = "ativado" if user.is_active else "desativado"
    return {"message": f"Usuário {user.name} {status}"}