"""Configuração dos testes — banco de teste separado."""

import sys
from pathlib import Path

# Adiciona raiz ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, get_db
from main import app

# Banco de teste (SQLite em memória — não afeta PostgreSQL)
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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
    """Registra usuário e retorna headers com token."""
    # Registrar
    client.post("/auth/register", json={
        "name": "Teste Admin",
        "email": "teste@teste.com",
        "password": "senha123",
        "role": "admin",
    })
    # Login
    resp = client.post("/auth/token", data={
        "username": "teste@teste.com",
        "password": "senha123",
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}