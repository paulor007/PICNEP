"""
Detecta oportunidades de economia comparando cotações e histórico.

Oportunidades detectadas:
1. Preço caiu vs última compra → comprar agora
2. Fornecedor mais barato que o habitual → trocar
3. Diferença grande entre fornecedores → renegociar com o caro
4. Concentração em um fornecedor → diversificar
5. Item sem cotação recente → pedir nova cotação
"""

from datetime import date, timedelta

from sqlalchemy.orm import Session

from models.quote import Quote
from models.purchase import Purchase
from models.item import Item
from models.supplier import Supplier
from models.alert import Alert


def detectar_oportunidades(db: Session, limite: int = 10) -> list[dict]:
    """
    Analisa todos os itens e detecta oportunidades de economia.

    Retorna lista de oportunidades ordenadas por economia potencial.
    """
    items = db.query(Item).all()
    oportunidades = []

    for item in items:
        opps = _analisar_item(db, item)
        oportunidades.extend(opps)

    # Ordenar por economia potencial (maior primeiro)
    oportunidades.sort(key=lambda x: x.get("economia_potencial", 0), reverse=True)

    return oportunidades[:limite]


def _analisar_item(db: Session, item: Item) -> list[dict]:
    """Analisa um item e retorna oportunidades encontradas."""
    opps = []

    # Cotações recentes (últimos 60 dias)
    data_limite = date.today() - timedelta(days=60)
    cotacoes = (
        db.query(Quote)
        .filter(Quote.item_id == item.id, Quote.date >= data_limite)
        .all()
    )

    # Última compra
    ultima_compra = (
        db.query(Purchase)
        .filter(Purchase.item_id == item.id, Purchase.status == "concluida")
        .order_by(Purchase.date.desc())
        .first()
    )

    if not cotacoes:
        # Item sem cotação recente
        opps.append({
            "item_id": item.id,
            "item_name": item.name,
            "type": "sem_cotacao",
            "severity": "warning",
            "message": f"{item.name}: sem cotação nos últimos 60 dias. Peça novas cotações.",
            "economia_potencial": 0,
        })
        return opps

    precos = [q.unit_price for q in cotacoes]
    menor_preco = min(precos)
    maior_preco = max(precos)

    # 1. Diferença grande entre fornecedores → renegociar
    if maior_preco > 0 and (maior_preco - menor_preco) / maior_preco > 0.10:
        economia = maior_preco - menor_preco
        fornecedor_barato = None
        for q in cotacoes:
            if q.unit_price == menor_preco:
                fornecedor_barato = db.query(Supplier).filter(
                    Supplier.id == q.supplier_id
                ).first()
                break

        opps.append({
            "item_id": item.id,
            "item_name": item.name,
            "type": "renegociar",
            "severity": "info",
            "message": (
                f"{item.name}: diferença de {((maior_preco - menor_preco) / maior_preco * 100):.0f}% "
                f"entre fornecedores. Melhor preço: R$ {menor_preco:.2f} "
                f"({fornecedor_barato.name if fornecedor_barato else 'N/A'})."
            ),
            "economia_potencial": round(economia, 2),
        })

    # 2. Preço caiu vs última compra → comprar agora
    if ultima_compra and menor_preco < ultima_compra.unit_price:
        queda = ultima_compra.unit_price - menor_preco
        queda_pct = (queda / ultima_compra.unit_price) * 100

        opps.append({
            "item_id": item.id,
            "item_name": item.name,
            "type": "preco_caiu",
            "severity": "info",
            "message": (
                f"{item.name}: preço caiu {queda_pct:.0f}% desde última compra "
                f"(de R$ {ultima_compra.unit_price:.2f} para R$ {menor_preco:.2f}). "
                f"Boa hora para comprar!"
            ),
            "economia_potencial": round(queda * (ultima_compra.quantity or 1), 2),
        })

    # 3. Preço subiu vs última compra → cuidado
    if ultima_compra and menor_preco > ultima_compra.unit_price * 1.05:
        alta = menor_preco - ultima_compra.unit_price
        alta_pct = (alta / ultima_compra.unit_price) * 100

        opps.append({
            "item_id": item.id,
            "item_name": item.name,
            "type": "preco_subiu",
            "severity": "warning",
            "message": (
                f"{item.name}: preço subiu {alta_pct:.0f}% desde última compra. "
                f"Considere renegociar ou buscar novos fornecedores."
            ),
            "economia_potencial": 0,
        })

    return opps


def gerar_alertas_banco(db: Session) -> int:
    """
    Detecta oportunidades e salva como alertas no banco.
    Retorna quantidade de alertas criados.
    """
    oportunidades = detectar_oportunidades(db, limite=20)
    criados = 0

    for opp in oportunidades:
        alert = Alert(
            item_id=opp.get("item_id"),
            type=opp["type"],
            severity=opp["severity"],
            message=opp["message"],
            data={"economia_potencial": opp.get("economia_potencial", 0)},
        )
        db.add(alert)
        criados += 1

    db.commit()
    return criados