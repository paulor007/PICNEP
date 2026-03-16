"""
Schemas de Fornecedor — validação de entrada e saída.

Imports:
- BaseModel (Pydantic): classe que valida dados automaticamente.
  Se o campo 'name' é str e alguém manda int, erro 422 automático.
  Se 'name' é obrigatório e não manda, erro 422 automático.

- Optional: campo que pode ser None (não obrigatório).
- Field: validação extra (min_length, ge=0, etc).

Por que 3 schemas para a mesma tabela?
- SupplierCreate: o que o usuário MANDA ao criar (sem id, sem created_at)
- SupplierUpdate: o que o usuário pode EDITAR (tudo opcional)
- SupplierResponse: o que a API RETORNA (com id, created_at)
"""

from datetime import datetime
from pydantic import BaseModel, Field

class SupplierCreate(BaseModel):
    """Schema para CRIAR fornecedor. Campos obrigatórios + opcionais."""
    name: str = Field(..., min_length=2, max_length=100, examples=["Materiais DF Ltda"])
    cnpj: str | None = Field(None, max_length=18, examples=["12.345.678/0001-90"])
    city: str = Field(..., min_length=2, max_length=100, examples=["Brasilia"])
    state: str = Field("DF", max_length=2, examples=["DF"])
    contact_name: str | None = Field(None, examples=["Paulo Lavarini"])
    contact_phone: str | None = Field(None, examples=["(61) 99999-0000"])
    contact_email: str | None = Field(None, examples=["paulolavarinio@materialdf.com"])
    avg_delivery_days: int = Field(7, ge=0, examples=[7])
    payment_terms: str = Field("30 dias", examples=["30 dias", "à vista", "28/56 dias"])

class SupplierUpdate(BaseModel):
    """Schema para EDITAR fornecedor. Tudo opcional (só manda o que mudar)."""
    name: str | None = None
    cnpj: str | None = None
    city: str | None = None
    state: str | None = None
    contact_name: str | None = None
    contact_phone: str | None = None
    contact_email: str | None = None
    avg_delivery_days: int | None = None
    payment_terms: str | None = None
    is_active: bool | None = None

class SupplierResponse(BaseModel):
    """Schema de RESPOSTA — o que a API retorna."""
    id: int
    name: str
    cnpj: str | None
    city: str
    state: str
    contact_name: str | None
    contact_phone: str | None
    contact_email: str | None
    avg_delivery_days: int
    payment_terms: str
    rating_score: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True # Permite converter SQLAlchemy model → Pydantic