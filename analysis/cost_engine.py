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
import re
from sqlalchemy.orm import Session

from models.quote import Quote
from models.supplier import Supplier

def calcular_custo_real(quote: Quote, taxa_capital: float = 0.02, taxa_espera: float = 0.005) -> dict:
    """
    Calcula custo real de uma cotação considerando todos os fatores.

    taxa_capital: custo mensal do capital (2% ao mês padrão para PME).
    taxa_espera: custo diário de espera pela entrega (0.5% do valor por dia).
    Representa custo de oportunidade: obra parada, equipe ociosa, etc.

    Retorna dict com breakdown completo.
    """
    # Converter para float — Numeric/Decimal do banco não opera com float nativo
    unit_price = float(quote.unit_price)
    quantity = int(quote.quantity)
    freight = float(quote.freight)

    custo_produto = unit_price * quantity
    custo_frete = freight
    custo_bruto = custo_produto + custo_frete

    # Custo financeiro do prazo de pagamento
    dias_pagamento = _extrair_dias_pagamento(quote.payment_term)
    beneficio_prazo = custo_bruto * taxa_capital * (dias_pagamento / 30)

    # Custo de espera pela entrega
    delivery_days = quote.delivery_days or 0
    custo_espera = custo_bruto * taxa_espera * delivery_days

    # Custo real = bruto - benefício do prazo + custo de espera
    custo_real = custo_bruto - beneficio_prazo + custo_espera

    # Custo unitário real
    custo_unitario_real = custo_real / quantity if quantity > 0 else 0

    return {
        "quote_id": quote.id,
        "custo_produto": round(custo_produto, 2),
        "custo_frete": round(custo_frete, 2),
        "custo_bruto": round(custo_bruto, 2),
        "dias_pagamento": dias_pagamento,
        "beneficio_prazo": round(beneficio_prazo, 2),
        "custo_real": round(custo_real, 2),
        "custo_unitario_real": round(custo_unitario_real, 4),
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
    
    # Pré-carregar todos os fornecedores de uma vez (1 query em vez de N)
    supplier_ids = {q.supplier_id for q in quotes}
    suppliers = {
        s.id: s 
        for s in db.query(Supplier).filter(Supplier.id.in_(supplier_ids)).all()
    }

    ranking = []
    for q in quotes:
        supplier = suppliers.get(q.supplier_id)
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
    nums = re.findall(r'\d+', term)
    if nums:
        return int(nums[0])
    return 0