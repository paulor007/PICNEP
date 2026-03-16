"""Schemas de Item de compra."""

from datetime import datetime
from pydantic import BaseModel, Field

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, examples=["Cimento CP-II 50kg"])
    category: str = Field(..., examples=["Material", "Ferramenta", "Serviço"])
    unit: str = Field("un", examples=["un", "kg", "saco", "m²", "litro"])
    description: str | None = Field(None, examples=["Cimento Portland composto"])
    min_stock: int = Field(0, ge=0)

class ItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    unit: str | None = None
    description: str | None = None
    min_stock: int | None = None

class ItemResponse(BaseModel):
    id: int
    name: str
    category: str
    unit: str
    description: str | None
    min_stock: int
    current_avg_price: float
    created_at: datetime

    class Config:
        from_attributes = True