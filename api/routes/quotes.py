"""Endpoints de cotações: CRUD + upload + comparação."""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user, require_role
from models.user import User
from models.quote import Quote
from models.supplier import Supplier
from models.item import Item
from schemas.quote import QuoteCreate, QuoteResponse, QuoteCompare
from services.upload_service import processar_upload_cotacoes

router = APIRouter(prefix="/api/v1/quotes", tags=["Cotações"])


@router.post("/", response_model=QuoteResponse, status_code=201)
def create_quote(
    data: QuoteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor")),
):
    """Registra cotação manualmente. Calcula total_cost automaticamente."""
    if not db.query(Item).filter(Item.id == data.item_id).first():
        raise HTTPException(status_code=404, detail="Item não encontrado")
    if not db.query(Supplier).filter(Supplier.id == data.supplier_id).first():
        raise HTTPException(status_code=404, detail="Fornecedor não encontrado")

    # Pega só os campos que existem no modelo Quote
    quote_data = data.model_dump(exclude={"valid_until"})
    total_cost = (data.unit_price * data.quantity) + data.freight

    quote = Quote(**quote_data, total_cost=total_cost)

    # Setar valid_until separadamente (se o modelo tiver)
    if hasattr(Quote, "valid_until") and data.valid_until:
        quote.valid_until = data.valid_until

    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


@router.post("/upload", status_code=200)
def upload_quotes(
    file: UploadFile = File(..., description="Planilha .xlsx ou .csv"),
    db: Session = Depends(get_db),
    user: User = Depends(require_role("admin", "gestor")),
):
    """Upload de planilha de cotações. Colunas obrigatórias: item_id, supplier_id, unit_price."""
    return processar_upload_cotacoes(file, db)


@router.get("/", response_model=list[QuoteResponse])
def list_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    item_id: int | None = Query(None),
    supplier_id: int | None = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Lista cotações com filtros."""
    query = db.query(Quote)
    if item_id:
        query = query.filter(Quote.item_id == item_id)
    if supplier_id:
        query = query.filter(Quote.supplier_id == supplier_id)
    return query.order_by(Quote.date.desc()).offset(skip).limit(limit).all()


@router.get("/compare/{item_id}", response_model=list[QuoteCompare])
def compare_quotes(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Compara fornecedores por custo real para um item. Ordenado: menor custo primeiro."""
    quotes = (
        db.query(Quote, Supplier.name)
        .join(Supplier, Quote.supplier_id == Supplier.id)
        .filter(Quote.item_id == item_id)
        .order_by(Quote.date.desc())
        .limit(20)
        .all()
    )
    if not quotes:
        raise HTTPException(status_code=404, detail="Nenhuma cotação para este item")

    result = []
    for quote, supplier_name in quotes:
        cost_per_unit = round(quote.total_cost / max(quote.quantity, 1), 2)
        result.append(QuoteCompare(
            supplier_name=supplier_name, unit_price=quote.unit_price,
            freight=quote.freight, delivery_days=quote.delivery_days,
            payment_term=quote.payment_term, total_cost=quote.total_cost,
            cost_per_unit=cost_per_unit, date=quote.date,
        ))
    result.sort(key=lambda x: x.cost_per_unit)
    return result