import os
from fastapi.testclient import TestClient
from app.main import app
from app.logic import calculate_emi

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_finds_loan_docs():
    response = client.post("/search", json={"question": "home loan documents"})
    assert response.status_code == 200
    ids = [doc["id"] for doc in response.json()["documents"]]
    assert "POL-001" in ids


def test_bad_input_is_rejected():
    response = client.post("/search", json={"question": "a"})
    assert response.status_code == 422


def test_zero_rate_emi():
    assert calculate_emi(12000, 0, 1) == 1000


def test_negative_rate_rejected():
    response = client.post("/emi", json={"principal": 5000, "annual_rate": -1, "years": 1})
    assert response.status_code == 422


def test_chat_requires_auth(monkeypatch):
    monkeypatch.setenv("APP_ACCESS_TOKEN", "secret-demo")
    response = client.post("/chat", json={"question": "home loan documents"})
    assert response.status_code == 401
