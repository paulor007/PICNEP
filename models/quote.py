"""
Modelo de cotação — o coração do PICNEP.

Uma cotação é uma proposta de preço de um fornecedor para um item.
O comprador recebe 3 cotações e compara. O PICNEP faz essa
comparação calculando custo real (preço + frete + condição).

Imports:
- ForeignKey: cria relação no banco. quote.item_id referencia items.id.
  O banco garante integridade: não permite cotação sem item válido.

total_cost: campo calculado (preço * quantidade + frete).
O engine de custo real usa esse campo para rankings e comparativos.
"""

from sqlalchemy import Column, Integer, Numeric, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from core.database import Base


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    unit_price = Column(Numeric(12, 4), nullable=False)            # Preço unitário
    freight = Column(Numeric(12, 2), default=0.0)                   # Frete
    delivery_days = Column(Integer, default=7)             # Prazo de entrega (dias)
    payment_term = Column(String(50), default="à vista")   # Condição: à vista, 30 dias, etc
    min_quantity = Column(Integer, default=1)               # Quantidade mínima
    quantity = Column(Integer, default=1)                   # Quantidade cotada
    total_cost = Column(Numeric(14, 2), default=0.0)                # Calculado: (unit_price * qty) + freight
    valid_until = Column(Date, nullable=True)               # Validade da cotação
    date = Column(Date, nullable=False)                     # Data da cotação
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    item = relationship("Item", back_populates="quotes")
    supplier = relationship("Supplier", back_populates="quotes")

    def __repr__(self):
        return f"<Quote(id={self.id}, item_id={self.item_id}, supplier='{self.supplier_id}', total={self.total_cost})>"