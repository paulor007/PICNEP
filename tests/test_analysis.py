"""Testes da engine de análise."""


def test_recommendations_empty(client, auth_headers):
    resp = client.get("/api/v1/analysis/recommendations", headers=auth_headers)
    assert resp.status_code == 200


def test_opportunities_empty(client, auth_headers):
    resp = client.get("/api/v1/analysis/opportunities", headers=auth_headers)
    assert resp.status_code == 200