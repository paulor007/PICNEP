"""
Conexão com PostgreSQL via SQLAlchemy.

Diferença do último projeto:
- PostgreSQL em vez de SQLite
- create_engine com pool de conexões (múltiplos usuários)
- get_db() como dependency injection do FastAPI

Imports:
- create_engine: cria conexão com o banco. A URL define qual banco
  (postgresql:// = PostgreSQL, sqlite:// = SQLite). O engine gerencia
  um pool de conexões para não abrir/fechar toda hora.

- sessionmaker: fábrica de sessões. Cada request da API usa uma sessão
  própria, que é fechada automaticamente no final.

- declarative_base: classe-mãe de todos os modelos (igual SARE).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Testa conexão antes de usar (evita "connection closed")
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Dependency injection para FastAPI.

    Como funciona:
    - FastAPI chama get_db() automaticamente para cada request
    - yield entrega a sessão para o endpoint usar
    - finally fecha a sessão (mesmo se der erro)

    No SARE: criava sessão manual (Session())
    No PICNEP: FastAPI gerencia automaticamente (Depends(get_db))
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()