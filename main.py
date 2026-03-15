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

app = FastAPI(
    title="PICNEP",
    description="Plataforma de Inteligência de Compras, Negociação e Economia Potencial",
    version="1.0.0",
)

# CORS (permite frontend acessar a API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Endpoint raiz — verifica se API está no ar."""
    return {
        "sistema": "PICNEP",
        "empresa": settings.EMPRESA_NOME,
        "status": "operacional",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    """Health check — usado por monitoramento e deploy."""
    return {"status": "ok"}