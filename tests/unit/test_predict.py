from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_valid():
    payload = {
        "age": 35,
        "monthly_income": 4000,
        "job_level": 2
    }

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert "probability" in data


def test_predict_invalid_age():
    payload = {
        "age": 10,
        "monthly_income": 4000,
        "job_level": 2
    }

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422