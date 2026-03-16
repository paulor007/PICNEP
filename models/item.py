"""
Modelo de item de compra (produto/insumo).

Por que separar item de produto?
- No SARE, "produto" era o que a empresa VENDE
- No PICNEP, "item" é o que a empresa COMPRA
- Nomenclatura diferente evita confusão conceitual

min_stock: estoque mínimo. Quando chega perto, o sistema pode alertar.
unit: unidade de medida (kg, un, m², saco, etc).
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from sqlalchemy.orm import relationship

from core.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # Material, Ferramenta, Serviço
    unit = Column(String(20), nullable=False, default="un")  # un, kg, m², saco, litro
    description = Column(String(255), nullable=True)
    min_stock = Column(Integer, default=0)
    current_avg_price = Column(Float, default=0.0)  # Atualizado pelo engine
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamentos
    quotes = relationship("Quote", back_populates="item")
    purchases = relationship("Purchase", back_populates="item")
    alerts = relationship("Alert", back_populates="item")

    def __repr__(self):
        return f"<Item(id={self.id}, name='{self.name}', unit='{self.unit}')>"