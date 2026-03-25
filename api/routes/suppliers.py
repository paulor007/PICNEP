"""
Endpoints CRUD de fornecedores.

CRUD = Create, Read, Update, Delete
  POST   /api/v1/suppliers       → Create  (admin, gestor)
  GET    /api/v1/suppliers       → Read    (autenticado)
  GET    /api/v1/suppliers/{id}  → Read    (autenticado)
  PUT    /api/v1/suppliers/{id}  → Update  (admin, gestor)
  DELETE /api/v1/suppliers/{id}  → Delete  (admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user, require_role
from models.user import User
from models.supplier import Supplier
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(prefix="/api/v1/suppliers", tags=["Fornecedores"])


@router.post("/", response_model=SupplierResponse, status_code=201)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor")),
):
    """Cadastra novo fornecedor. Requer: admin ou gestor."""
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/", response_model=list[SupplierResponse])
def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Lista fornecedores. Requer: autenticado."""
    query = db.query(Supplier)
    if active_only:
        query = query.filter(Supplier.is_active.is_(True))
    return query.offset(skip).limit(limit).all()


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Retorna fornecedor pelo ID. Requer: autenticado."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return supplier


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor")),
):
    """Atualiza fornecedor. Requer: admin ou gestor."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier


@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin")),
):
    """Remove fornecedor (soft delete). Requer: admin."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    supplier.is_active = False
    db.commit()