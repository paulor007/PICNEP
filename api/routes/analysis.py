"""
Endpoints de análise — a inteligência do PICNEP.

Estes endpoints transformam dados brutos em decisão.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.user import User
from models.item import Item
from analysis.cost_engine import ranking_fornecedores_por_item
from analysis.opportunity_detector import detectar_oportunidades, gerar_alertas_banco
from analysis.recommendation import recomendar_item, recomendar_todos

router = APIRouter(prefix="/api/v1/analysis", tags=["Análise e Inteligência"])


@router.get("/cost/{item_id}")
def get_cost_ranking(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Ranking de fornecedores por CUSTO REAL para um item.
    Considera: preço + frete + condição de pagamento.
    """
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    ranking = ranking_fornecedores_por_item(db, item_id)

    return {
        "item_id": item_id,
        "item_name": item.name,
        "ranking": ranking,
        "total_cotacoes": len(ranking),
    }


@router.get("/opportunities")
def get_opportunities(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Detecta oportunidades de economia em todos os itens.
    Ordenadas por economia potencial (maior primeiro).
    """
    return {
        "opportunities": detectar_oportunidades(db),
    }


@router.get("/recommendations")
def get_recommendations(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Recomendação para todos os itens: comprar agora, esperar ou renegociar.
    """
    return {
        "recommendations": recomendar_todos(db),
    }


@router.get("/recommendations/{item_id}")
def get_item_recommendation(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Recomendação para um item específico."""
    return recomendar_item(db, item_id)


@router.post("/alerts/generate")
def generate_alerts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Detecta oportunidades e salva como alertas no banco."""
    count = gerar_alertas_banco(db)
    return {"message": f"{count} alertas gerados", "total": count}