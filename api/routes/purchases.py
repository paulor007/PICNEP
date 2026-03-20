"""Endpoints de compras realizadas (histórico)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user, require_role
from models.user import User
from models.purchase import Purchase
from models.item import Item
from models.supplier import Supplier
from schemas.purchase import PurchaseCreate, PurchaseResponse

router = APIRouter(prefix="/api/v1/purchases", tags=["Compras"])


@router.post("/", response_model=PurchaseResponse, status_code=201)
def create_purchase(
    data: PurchaseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor")),
):
    """Registra compra realizada."""
    if not db.query(Item).filter(Item.id == data.item_id).first():
        raise HTTPException(status_code=404, detail="Item não encontrado")
    if not db.query(Supplier).filter(Supplier.id == data.supplier_id).first():
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    total_cost = round((data.unit_price * data.quantity) + data.freight, 2)
    purchase = Purchase(**data.model_dump(), total_cost=total_cost)
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    return purchase


@router.get("/", response_model=list[PurchaseResponse])
def list_purchases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    item_id: int | None = Query(None),
    supplier_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Lista compras com filtros."""
    query = db.query(Purchase)
    if item_id:
        query = query.filter(Purchase.item_id == item_id)
    if supplier_id:
        query = query.filter(Purchase.supplier_id == supplier_id)
    return query.order_by(Purchase.date.desc()).offset(skip).limit(limit).all()


@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Retorna compra pelo ID."""
    purchase = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Compra não encontrada")
    return purchase