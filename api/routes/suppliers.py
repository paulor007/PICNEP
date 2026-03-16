"""
Endpoints CRUD de fornecedores.

Imports:
- APIRouter: cria grupo de rotas.
  Cada router é registrado no app principal com um prefixo.

- Depends: injeta get_db automaticamente.

- HTTPException: retorna erros HTTP formatados (404, 400, etc).

CRUD = Create, Read, Update, Delete
  POST   /api/v1/suppliers       → Create
  GET    /api/v1/suppliers       → Read (lista)
  GET    /api/v1/suppliers/{id}  → Read (detalhe)
  PUT    /api/v1/suppliers/{id}  → Update
  DELETE /api/v1/suppliers/{id}  → Delete
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db
from models.supplier import Supplier
from schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse

router = APIRouter(prefix="/api/v1/suppliers", tags=["Fornecedores"])

@router.post("/", response_model=SupplierResponse, status_code=201)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    """
    Cadastra novo fornecedor.

    O FastAPI valida 'data' automaticamente com SupplierCreate.
    Se faltar campo obrigatório ou tipo errado → 422 automático.
    """
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)  # Recarrega com id e created_at do banco
    return supplier

@router.get("/", response_model=list[SupplierResponse])
def list_suppliers(
    skip: int = Query(0, ge=0, description="Pular N registros"),
    limit: int = Query(50, ge=1, le=100, description="Máximo de registros"),
    active_only: bool = Query(True, description="Apenas ativos"),
    db: Session = Depends(get_db),
):
    """
    Lista fornecedores com paginação.

    Por que paginação?
    - Se tiver 1000 fornecedores, retornar tudo é lento
    - skip=0, limit=50 retorna os 50 primeiros
    - skip=50, limit=50 retorna os próximos 50
    """
    query = db.query(Supplier)
    if active_only:
        query = query.filter(Supplier.is_active_(True))
    return query.offset(skip).limit(limit).all()

@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Retorna fornecedor pelo ID."""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")
    return supplier

@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, data: SupplierUpdate, db: Session = Depends(get_db)):
    """
    Atualiza fornecedor. Só envia os campos que quer mudar.

    model_dump(exclude_unset=True) retorna apenas os campos enviados.
    Campos não enviados NÃO são alterados (não sobrescreve com None).
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(supplier, field, value)

    db.commit()
    db.refresh(supplier)
    return supplier

@router.delete("/{supplier_id}", status_code=204)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """
    Remove fornecedor (soft delete — marca como inativo).

    Por que soft delete?
    - Deletar de verdade apaga histórico de compras
    - Marcar como inativo preserva dados para relatórios
    """
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    supplier.is_active = False
    db.commit()