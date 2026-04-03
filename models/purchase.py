"""
Modelo de compra realizada (histórico).

Diferença entre Quote e Purchase:
- Quote = proposta (fornecedor oferece preço)
- Purchase = compra concluída (empresa pagou)

O histórico permite responder:
- "Quanto paguei nesse item nos últimos 6 meses?"
- "Qual fornecedor tem melhor preço histórico?"
- "Estou pagando mais caro que antes?"
"""

from sqlalchemy import Column, Integer, Numeric, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from core.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=True)  # Opcional: qual cotação virou compra
    date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 4), nullable=False)
    freight = Column(Numeric(12, 4), default=0.0)
    total_cost = Column(Numeric(12, 4), nullable=False)  # (unit_price * quantity) + freight
    payment_term = Column(String(50), default="à vista")
    status = Column(String(20), default="concluida")  # concluida, pendente, cancelada
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    item = relationship("Item", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")

    def __repr__(self):
        return f"<Purchase(id={self.id}, item_id={self.item_id}, total={self.total_cost})>"