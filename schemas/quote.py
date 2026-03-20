"""
Schemas de Cotação — o dado mais importante do PICNEP.

total_cost é calculado automaticamente:
  total_cost = (unit_price * quantity) + freight
"""

from datetime import date as DateType, datetime as DateTimeType
from pydantic import BaseModel, Field

class QuoteCreate(BaseModel):
    item_id: int = Field(..., examples=[1])
    supplier_id: int = Field(..., examples=[1])
    unit_price: float = Field(..., gt=0, examples=[49.90])
    freight: float = Field(0.0, ge=0, examples=[150.00])
    delivery_days: int = Field(7, ge=0, examples=[7])
    payment_term: str = Field("à vista", examples=["à vista", "30 dias"])
    min_quantity: int = Field(1, ge=1, examples=[10])
    quantity: int = Field(1, ge=1, examples=[100])
    valid_until: DateType | None = Field(None, examples=["2026-04-30"])
    date: DateType = Field(..., examples=["2026-03-19"])
    notes: str | None = Field(None, examples=["Preço especial"])

class QuoteResponse(BaseModel):
    id: int
    item_id: int
    supplier_id: int
    unit_price: float
    freight: float
    delivery_days: int
    payment_term: str
    min_quantity: int
    quantity: int
    total_cost: float
    valid_until: DateType | None
    date: DateType
    notes: str | None
    created_at: DateTimeType

    class Config: 
        from_attributes = True

class QuoteCompare(BaseModel):
    """Comparação de cotações de um mesmo item."""
    supplier_name: str
    unit_price: float
    freight: float
    delivery_days: int
    payment_term: str
    total_cost: float
    cost_per_unit: float  # total_cost / quantity (custo real unitário)
    date: DateType