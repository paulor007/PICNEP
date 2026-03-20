"""Exporta todos os routers."""

from api.routes.suppliers import router as suppliers_router
from api.routes.items import router as items_router
from api.routes.quotes import router as quotes_router
from api.routes.purchases import router as purchases_router

__all__ = ["suppliers_router", "items_router", "quotes_router", "purchases_router"]