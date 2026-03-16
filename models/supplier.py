"""
Modelo de fornecedor.

Imports:
- relationship: cria atalho Python entre tabelas.
  supplier.quotes retorna todas cotações desse fornecedor
  sem escrever SQL. O back_populates conecta os dois lados.

- Float: tipo decimal. Usado para rating_score (0.0 a 5.0).

Por que guardar avg_delivery_days e payment_terms?
- O custo real de uma compra não é só preço unitário
- Frete (avg_delivery_days influencia custo logístico)
- Prazo de pagamento (30 dias = capital de giro)
- O engine de custo real usa esses campos para calcular custo efetivo
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    cnpj = Column(String(18), unique=True, nullable=True)  # Opcional para demo
    city = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False, default="MG")
    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(150), nullable=True)
    avg_delivery_days = Column(Integer, default=7)  # Prazo médio de entrega
    payment_terms = Column(String(50), default="30 dias")  # Condição de pagamento
    rating_score = Column(Float, default=0.0)  # 0.0 a 5.0 (calculado pelo sistema)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    quotes = relationship("Quote", back_populates="supplier")
    purchases = relationship("Purchase", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}', city='{self.city}')>"