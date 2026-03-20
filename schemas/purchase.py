"""Schemas de Compra realizada (histórico)."""

from datetime import date as DateType, datetime as DateTimeType
from pydantic import BaseModel, Field

class PurchaseCreate(BaseModel):
    item_id: int = Field(..., examples=[1])
    supplier_id: int = Field(..., examples=[1])
    quote_id: int | None = Field(None, examples=[1])
    date: DateType = Field(..., examples=["2026-03-19"])
    quantity: int = Field(..., ge=1, examples=[100])
    unit_price: float = Field(..., gt=0, examples=[49.90])
    freight: float = Field(0.0, ge=0, examples=[150.00])
    payment_term: str = Field("à vista", examples=["à vista", "30 dias"])
    notes: str | None = None

class PurchaseResponse(BaseModel):
    id: int
    item_id: int
    supplier_id: int
    quote_id: int | None
    date: DateType
    quantity: int
    unit_price: float
    freight: float
    total_cost: float
    payment_term: str
    status: str
    notes: str | None
    created_at: DateTimeType

    class Config:
        from_attributes = True