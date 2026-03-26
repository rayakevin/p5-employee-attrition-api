"""Tests unitaires des endpoints de disponibilite de l'API."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    """Verifie que la racine repond avec un message simple."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API is running"}


def test_health() -> None:
    """Verifie que l'endpoint de sante expose un statut nominal."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
