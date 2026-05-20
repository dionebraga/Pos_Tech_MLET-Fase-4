"""Testes de integração da API (sem precisar do modelo treinado)."""
from fastapi.testclient import TestClient

from src.api.main import app


def test_root_endpoint():
    with TestClient(app) as client:
        r = client.get("/")
        assert r.status_code == 200
        assert "name" in r.json()
        assert "version" in r.json()


def test_health_endpoint():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert "status" in body
        assert "model_loaded" in body


def test_metrics_endpoint_exposed():
    with TestClient(app) as client:
        r = client.get("/metrics")
        assert r.status_code == 200
        # Métricas Prometheus são texto plano
        assert "http_requests_total" in r.text or "python_info" in r.text


def test_predict_validates_input():
    with TestClient(app) as client:
        # Lista vazia deve retornar erro de validação
        r = client.post("/predict", json={"close_prices": []})
        assert r.status_code == 422


def test_predict_validates_negative_prices():
    with TestClient(app) as client:
        r = client.post("/predict", json={"close_prices": [100.0, -1.0, 102.0]})
        assert r.status_code == 422


def test_predict_validates_days_ahead_range():
    with TestClient(app) as client:
        r = client.post(
            "/predict",
            json={"close_prices": [100.0] * 100, "days_ahead": 100},
        )
        # > 30 deve falhar na validação
        assert r.status_code == 422
