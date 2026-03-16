"""Exporta todos os routers."""

from api.routes.suppliers import router as suppliers_router
from api.routes.items import router as items_router

__all__ = ["suppliers_router", "items_router"]