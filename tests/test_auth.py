"""Testes de autenticação."""


def test_register_success(client):
    resp = client.post("/auth/register", json={
        "name": "Novo User", "email": "novo@teste.com",
        "password": "senha123", "role": "analista",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "novo@teste.com"
    assert "password" not in resp.json()


def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "name": "User 1", "email": "dup@teste.com",
        "password": "senha123", "role": "admin",
    })
    resp = client.post("/auth/register", json={
        "name": "User 2", "email": "dup@teste.com",
        "password": "senha456", "role": "admin",
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "name": "Login Test", "email": "login@teste.com",
        "password": "senha123", "role": "admin",
    })
    resp = client.post("/auth/token", data={
        "username": "login@teste.com", "password": "senha123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "name": "Wrong", "email": "wrong@teste.com",
        "password": "senha123", "role": "admin",
    })
    resp = client.post("/auth/token", data={
        "username": "wrong@teste.com", "password": "errada",
    })
    assert resp.status_code == 401