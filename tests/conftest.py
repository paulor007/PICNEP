# tests/conftest.py

"""Configuração dos testes — banco de teste separado."""

import sys
from pathlib import Path

# Adiciona raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool  # ← NOVO: força conexão única

from core.database import Base, get_db
from core.security import hash_password   # ← NOVO: para criar admin direto
from models.user import User              # ← NOVO: para criar admin direto
from main import app

# Banco de teste (SQLite em memória)
# StaticPool = todas as conexões usam o MESMO banco em memória
# Sem ele, cada conexão abre um banco vazio separado → "no such table"
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # ← NOVO: resolve "no such table"
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


# Sobrescreve dependência do banco nos testes
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    """Cria tabelas antes de cada teste, limpa depois."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """TestClient do FastAPI."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Cria usuário admin DIRETO no banco e retorna headers com token.

    Por que não usar /auth/register?
    Porque /register agora força role='analista' (segurança).
    Testes que precisam de admin (suppliers, analysis) não funcionariam.
    Criar direto no banco garante role='admin'.
    """
    # Criar admin direto no banco (sem passar pelo /register)
    db = TestSession()
    admin = User(
        name="Teste Admin",
        email="teste@teste.com",
        password_hash=hash_password("senha123"),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.close()

    # Login normal via API (isso funciona com qualquer role)
    resp = client.post("/auth/token", data={
        "username": "teste@teste.com",
        "password": "senha123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}