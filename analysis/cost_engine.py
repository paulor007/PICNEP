"""
Engine de custo real — calcula custo efetivo de compra.

O preço unitário NÃO é o custo real. O custo real inclui:
- Preço unitário x quantidade
- Frete
- Custo financeiro do prazo de pagamento (dinheiro parado)
- Custo de espera (prazo de entrega afeta operação)

Exemplo:
  Fornecedor A: R$ 48/un + R$ 0 frete + à vista + 3 dias
  Fornecedor B: R$ 46/un + R$ 200 frete + 30 dias + 7 dias
  Para 100 unidades:
    A: 48*100 + 0 = R$ 4.800 (recebe rápido, paga hoje)
    B: 46*100 + 200 = R$ 4.800 (paga em 30 dias = capital de giro)
    → B é melhor: mesmo custo, mas paga depois!
"""

from sqlalchemy.orm import Session

from models.quote import Quote
from models.supplier import Supplier

def calcular_custo_real(quote: Quote, taxa_capital: float = 0.02) -> dict:
    """
    Calcula custo real de uma cotação considerando todos os fatores.

    taxa_capital: custo mensal do capital (2% ao mês padrão para PME).
    Se paga à vista, perde esse rendimento.
    Se paga em 30 dias, "ganha" esse valor.

    Retorna dict com breakdown completo.
    """
    custo_produto = quote.unit_price * quote.quantity
    custo_frete = quote.freight
    custo_bruto = custo_produto + custo_frete

    # Custo financeiro do prazo de pagamento
    dias_pagamento = _extrair_dias_pagamento(quote.payment_term)
    beneficio_prazo = custo_bruto * taxa_capital * (dias_pagamento / 30)

    # Custo real = bruto - benefício do prazo
    custo_real = custo_bruto - beneficio_prazo

    # Custo unitário real
    custo_unitario_real = custo_real / quote.quantity if quote.quantity > 0 else 0

    return {
        "quote_id": quote.id,
        "custo_produto": round(custo_produto, 2),
        "custo_frete": round(custo_frete, 2),
        "custo_bruto": round(custo_bruto, 2),
        "dias_pagamento": dias_pagamento,
        "beneficio_prazo": round(beneficio_prazo, 2),
        "custo_real": round(custo_real, 2),
        "custo_unitario_real": round(custo_unitario_real, 4),
        "delivery_days": quote.delivery_days,
    }

def ranking_fornecedores_por_item(db: Session, item_id: int) -> list[dict]:
    """
    Ranking de fornecedores para um item pelo CUSTO REAL.

    Retorna lista ordenada: melhor custo real primeiro.
    Inclui nome do fornecedor e breakdown do custo.
    """
    quotes = (
        db.query(Quote)
        .filter(Quote.item_id == item_id)
        .order_by(Quote.date.desc())
        .all()
    )

    if not quotes:
        return []

    ranking = []
    for q in quotes:
        supplier = db.query(Supplier).filter(Supplier.id == q.supplier_id).first()
        custo = calcular_custo_real(q)
        custo["supplier_name"] = supplier.name if supplier else "Desconhecido"
        custo["supplier_id"] = q.supplier_id
        custo["date"] = str(q.date)
        ranking.append(custo)

    # Ordenar por custo real (menor primeiro)
    ranking.sort(key=lambda x: x["custo_real"])

    return ranking


def _extrair_dias_pagamento(payment_term: str) -> int:
    """Extrai dias de pagamento da condição. Ex: '30 dias' → 30."""
    if not payment_term:
        return 0
    term = str(payment_term).lower().strip()
    if "vista" in term:
        return 0
    # Extrair números
    import re
    nums = re.findall(r'\d+', term)
    if nums:
        return int(nums[0])
    return 0