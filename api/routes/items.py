"""
Endpoints CRUD de itens de compra.

  POST   /api/v1/items       → Create  (admin, gestor)
  GET    /api/v1/items       → Read    (autenticado)
  GET    /api/v1/items/{id}  → Read    (autenticado)
  PUT    /api/v1/items/{id}  → Update  (admin, gestor)
  DELETE /api/v1/items/{id}  → Delete  (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user, require_role
from models.user import User
from models.item import Item
from schemas.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter(prefix="/api/v1/items", tags=["Itens"])


@router.post("/", response_model=ItemResponse, status_code=201)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor")),
):
    """Cadastra novo item. Requer: admin ou gestor."""
    item = Item(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[ItemResponse])
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: str | None = Query(None, description="Filtrar por categoria"),
    active_only: bool = Query(True, description="Retornar apenas itens ativos"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Lista itens. Requer: autenticado."""
    query = db.query(Item)
    if active_only:
        query = query.filter(Item.is_active_(True))
    if category:
        query = query.filter(Item.category == category)
    return query.offset(skip).limit(limit).all()


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retorna item pelo ID. Requer: autenticado."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor")),
):
    """Atualiza item. Requer: admin ou gestor."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """
    Remove item. Requer: admin.
    
    Por que soft delete e não hard delete?
    Itens têm cotações e compras vinculadas na tabela quotes e purchases
    (via ForeignKey). Se apagar o item fisicamente, o banco rejeita
    a operação com erro de FK violation. O soft delete preserva o histórico.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")
    item.is_active = False
    db.commit()