"""
PICNEP — Ponto de entrada da API FastAPI.

Diferença em relação o último projeto:
- SARE usava Click (CLI): python app.py status
- PICNEP usa FastAPI (API): GET /api/v1/status

Para rodar: uvicorn main:app --reload
Documentação automática: http://localhost:8000/docs

Imports:
- FastAPI: framework web que cria API REST automaticamente.
  Cada função decorada com @app.get() ou @app.post() vira um endpoint.
  A documentação Swagger é gerada automaticamente em /docs.

- uvicorn: servidor ASGI que roda o FastAPI. ASGI é o protocolo
  assíncrono do Python (evolução do WSGI usado por Flask/Django).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from api.auth.router import router as auth_router
from api.routes.suppliers import router as suppliers_router
from api.routes.items import router as items_router
from api.routes.quotes import router as quotes_router
from api.routes.purchases import router as purchases_router

app = FastAPI(
    title="PICNEP",
    description="Plataforma de Inteligência de Compras, Negociação e Economia Potencial",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Registrar rotas ──
app.include_router(auth_router)
app.include_router(suppliers_router)
app.include_router(items_router)
app.include_router(quotes_router)
app.include_router(purchases_router)

@app.get("/")
def root():
    """Endpoint raiz — verifica se API está no ar."""
    return {
        "sistema": "PICNEP",
        "empresa": settings.EMPRESA_NOME,
        "status": "operacional",
        "docs": "/docs",
    }


@app.get("/health", tags=["Sistema"])
def health():
    """Health check — usado por monitoramento."""
    return {"status": "ok"}