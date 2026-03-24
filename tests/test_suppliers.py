"""Testes de fornecedores."""


def test_create_supplier(client, auth_headers):
    resp = client.post("/api/v1/suppliers/", json={
        "name": "Fornecedor Teste", "city": "BH", "state": "MG",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Fornecedor Teste"


def test_list_suppliers(client, auth_headers):
    client.post("/api/v1/suppliers/", json={
        "name": "Forn 1", "city": "BH",
    }, headers=auth_headers)
    resp = client.get("/api/v1/suppliers/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_create_supplier_without_auth(client):
    resp = client.post("/api/v1/suppliers/", json={
        "name": "Sem Auth", "city": "SP",
    })
    assert resp.status_code == 401