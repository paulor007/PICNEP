"""
Modelo de alerta gerado pelo sistema.

Tipos de alerta:
- price_drop: preço caiu (oportunidade de compra)
- price_rise: preço subiu (cuidado)
- opportunity: economia potencial detectada
- renegotiate: item com margem para renegociar
- low_stock: estoque abaixo do mínimo
- supplier_risk: concentração em um fornecedor

severity:
- info: informativo (preço caiu 3%)
- warning: atenção (preço subiu 10%)
- critical: urgente (estoque zerado, fornecedor único)

data: campo JSON para detalhes adicionais sem criar colunas extras.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, func
from sqlalchemy.orm import relationship

from core.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    type = Column(String(30), nullable=False)      # price_drop, opportunity, renegotiate, etc
    severity = Column(String(10), nullable=False, default="info")  # info, warning, critical
    message = Column(String(500), nullable=False)
    data = Column(JSON, nullable=True)              # Detalhes extras em JSON
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relacionamento
    item = relationship("Item", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(id={self.id}, type='{self.type}', severity='{self.severity}')>"