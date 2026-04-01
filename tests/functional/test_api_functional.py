"""Tests fonctionnels du contrat public de l'API.

Ces tests se placent au niveau du parcours client :
- verification des routes ouvertes ;
- verification de la protection des routes metier ;
- verification de la documentation OpenAPI exposee.
"""

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


client = TestClient(app)
AUTH_HEADERS = {settings.api_key_header_name: settings.api_key}


def build_valid_payload() -> dict:
    """Construit un payload fonctionnel minimal complet."""
    return {
        "age": 35,
        "genre": "Homme",
        "revenu_mensuel": 4500,
        "statut_marital": "Marié(e)",
        "departement": "Consulting",
        "poste": "Consultant",
        "nombre_experiences_precedentes": 3,
        "annee_experience_totale": 12,
        "annees_dans_l_entreprise": 7,
        "annees_dans_le_poste_actuel": 4,
        "satisfaction_employee_environnement": 3,
        "note_evaluation_precedente": 3.0,
        "niveau_hierarchique_poste": 2,
        "satisfaction_employee_nature_travail": 4,
        "satisfaction_employee_equipe": 3,
        "satisfaction_employee_equilibre_pro_perso": 2,
        "note_evaluation_actuelle": 4.0,
        "heure_supplementaires": "Oui",
        "augementation_salaire_precedente": 0.12,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 3,
        "nombre_employee_sous_responsabilite": 0,
        "distance_domicile_travail": 12,
        "niveau_education": 3,
        "domaine_etude": "Infra & Cloud",
        "frequence_deplacement": "Occasionnel",
        "annees_depuis_la_derniere_promotion": 2,
        "annes_sous_responsable_actuel": 3,
    }


def test_public_routes_are_available_without_authentication() -> None:
    """Verifie que les routes techniques publiques restent ouvertes."""
    assert client.get("/").status_code == 200
    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_unknown_route_returns_404() -> None:
    """Verifie qu'une route inexistante renvoie bien 404."""
    assert client.get("/api/v1/unknown-route").status_code == 404


def test_wrong_http_method_returns_405() -> None:
    """Verifie qu'une methode HTTP non supportee renvoie 405."""
    assert client.get("/api/v1/predict").status_code == 405


def test_prediction_routes_require_api_key() -> None:
    """Verifie que les routes metier sont bien protegees."""
    payload = build_valid_payload()

    assert client.post("/api/v1/predict", json=payload).status_code == 401
    assert client.post("/api/v1/explain", json=payload).status_code == 401
    assert client.post("/api/v1/predict/batch", json={"rows": [payload]}).status_code == 401


def test_openapi_exposes_security_scheme_and_examples() -> None:
    """Verifie que Swagger documente la securite et les exemples d'appel."""
    schema = client.get("/openapi.json").json()

    security_schemes = schema["components"]["securitySchemes"]
    assert "APIKeyHeader" in security_schemes
    assert security_schemes["APIKeyHeader"]["type"] == "apiKey"

    prediction_input_schema = schema["components"]["schemas"]["PredictionInput"]
    assert "example" in prediction_input_schema

    predict_operation = schema["paths"]["/api/v1/predict"]["post"]
    assert {"APIKeyHeader": []} in predict_operation["security"]


def test_prediction_route_returns_422_for_invalid_payload() -> None:
    """Verifie qu'un payload invalide est rejete par la validation FastAPI."""
    payload = build_valid_payload()
    payload["age"] = 10

    response = client.post(
        "/api/v1/predict",
        json=payload,
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 422


def test_prediction_route_works_with_valid_api_key() -> None:
    """Verifie le parcours nominal sur la route unitaire protegee."""
    response = client.post(
        "/api/v1/predict",
        json=build_valid_payload(),
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200
    body = response.json()
    assert "prediction" in body
    assert "score" in body
