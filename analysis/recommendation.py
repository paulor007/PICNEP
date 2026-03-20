"""
Motor de recomendação: comprar agora, esperar ou renegociar.

Lógica:
- Se preço caiu vs histórico → COMPRAR AGORA
- Se preço subiu mas tem fornecedor mais barato → TROCAR FORNECEDOR
- Se diferença >10% entre fornecedores → RENEGOCIAR com o caro
- Se preço estável → COMPRAR (sem urgência)
- Se sem cotação recente → PEDIR NOVA COTAÇÃO
"""

from sqlalchemy.orm import Session

from models.purchase import Purchase
from models.item import Item
from analysis.cost_engine import ranking_fornecedores_por_item


def recomendar_item(db: Session, item_id: int) -> dict:
    """
    Gera recomendação de compra para um item.

    Retorna dict com:
    - acao: "comprar_agora", "esperar", "renegociar", "pedir_cotacao"
    - motivo: explicação
    - fornecedor_ideal: quem tem melhor custo real
    - economia_potencial: quanto pode economizar
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return {"erro": "Item não encontrado"}

    # Ranking por custo real
    ranking = ranking_fornecedores_por_item(db, item_id)

    if not ranking:
        return {
            "item_id": item_id,
            "item_name": item.name,
            "acao": "pedir_cotacao",
            "motivo": "Sem cotações disponíveis. Solicite cotações aos fornecedores.",
            "fornecedor_ideal": None,
            "economia_potencial": 0,
        }

    melhor = ranking[0]

    # Última compra
    ultima_compra = (
        db.query(Purchase)
        .filter(Purchase.item_id == item_id, Purchase.status == "concluida")
        .order_by(Purchase.date.desc())
        .first()
    )

    # Analisar
    if not ultima_compra:
        return {
            "item_id": item_id,
            "item_name": item.name,
            "acao": "comprar_agora",
            "motivo": (
                f"Primeira compra. Melhor custo real: {melhor['supplier_name']} "
                f"(R$ {melhor['custo_unitario_real']:.2f}/un)."
            ),
            "fornecedor_ideal": melhor["supplier_name"],
            "economia_potencial": 0,
        }

    # Comparar com última compra
    preco_anterior = ultima_compra.unit_price
    preco_atual = melhor["custo_unitario_real"]
    variacao = ((preco_atual - preco_anterior) / preco_anterior) * 100

    if variacao <= -5:
        # Preço caiu 5%+ → comprar agora
        economia = (preco_anterior - preco_atual) * (ultima_compra.quantity or 100)
        return {
            "item_id": item_id,
            "item_name": item.name,
            "acao": "comprar_agora",
            "motivo": (
                f"Preço caiu {abs(variacao):.0f}% desde última compra! "
                f"De R$ {preco_anterior:.2f} para R$ {preco_atual:.2f}/un. "
                f"Fornecedor: {melhor['supplier_name']}."
            ),
            "fornecedor_ideal": melhor["supplier_name"],
            "economia_potencial": round(economia, 2),
        }

    elif variacao >= 10:
        # Preço subiu 10%+ → renegociar
        return {
            "item_id": item_id,
            "item_name": item.name,
            "acao": "renegociar",
            "motivo": (
                f"Preço subiu {variacao:.0f}% desde última compra. "
                f"Negocie com {melhor['supplier_name']} ou busque alternativas."
            ),
            "fornecedor_ideal": melhor["supplier_name"],
            "economia_potencial": 0,
        }

    else:
        # Preço estável
        return {
            "item_id": item_id,
            "item_name": item.name,
            "acao": "comprar_agora",
            "motivo": (
                f"Preço estável (variação {variacao:+.0f}%). "
                f"Melhor custo real: {melhor['supplier_name']} "
                f"(R$ {preco_atual:.2f}/un)."
            ),
            "fornecedor_ideal": melhor["supplier_name"],
            "economia_potencial": 0,
        }


def recomendar_todos(db: Session) -> list[dict]:
    """Gera recomendação para todos os itens."""
    items = db.query(Item).all()
    return [recomendar_item(db, item.id) for item in items]