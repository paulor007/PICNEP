"""Endpoints de alertas."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from models.user import User
from models.alert import Alert

router = APIRouter(prefix="/api/v1/alerts", tags=["Alertas"])


@router.get("/")
def list_alerts(
    unread_only: bool = Query(False, description="Apenas não lidos"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Lista alertas ativos."""
    query = db.query(Alert).order_by(Alert.created_at.desc())
    if unread_only:
        query = query.filter(Alert.is_read.is_(False))
    alerts = query.limit(50).all()

    return {
        "alerts": [
            {
                "id": a.id,
                "type": a.type,
                "severity": a.severity,
                "message": a.message,
                "data": a.data,
                "is_read": a.is_read,
                "created_at": str(a.created_at),
            }
            for a in alerts
        ],
        "total": len(alerts),
    }


@router.put("/{alert_id}/read")
def mark_as_read(
    alert_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Marca alerta como lido."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if alert:
        alert.is_read = True
        db.commit()
    return {"message": "Alerta marcado como lido"}