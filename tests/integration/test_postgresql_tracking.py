"""Tests d'integration PostgreSQL executes sur le moteur cible.

Ces tests ne sont pas destines au cycle local par defaut. Ils s'activent
explicitement en CI pour verifier que PostgreSQL applique bien les
contraintes du schema et que les scripts de seed tournent sur le vrai moteur.
"""

from __future__ import annotations

import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import delete, func, inspect, select
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.db.models import ApiAuditLog, EmployeeSource, PredictionRequest, PredictionResult
from app.db.session import SessionLocal, engine, get_db
from app.main import app
import scripts.seed_data as seed_data


pytestmark = pytest.mark.skipif(
    os.getenv("P5_RUN_POSTGRES_INTEGRATION") != "1",
    reason="Tests PostgreSQL reels reserves a la CI ou aux executions explicites.",
)

client = TestClient(app)
AUTH_HEADERS = {settings.api_key_header_name: settings.api_key}


def build_valid_payload() -> dict:
    """Construit un payload metier complet pour le flux PostgreSQL reel."""
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
        "augementation_salaire_precedente": 12,
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


@pytest.fixture(autouse=True)
def use_real_postgresql_database():
    """Force ce module a utiliser la vraie base PostgreSQL configuree."""
    assert settings.database_url.startswith("postgresql")

    original_overrides = dict(app.dependency_overrides)
    app.dependency_overrides.pop(get_db, None)

    with SessionLocal() as db:
        db.execute(delete(ApiAuditLog))
        db.execute(delete(PredictionResult))
        db.execute(delete(PredictionRequest))
        db.commit()

    try:
        yield
    finally:
        app.dependency_overrides = original_overrides


def test_seed_employee_source_reloads_rows_on_postgresql() -> None:
    """Verifie le seed complet sur PostgreSQL reel."""
    inserted_rows = seed_data.seed_employee_source()
    inspector = inspect(engine)

    with SessionLocal() as db:
        row_count = db.scalar(select(func.count()).select_from(EmployeeSource))

    assert inserted_rows == 1470
    assert row_count == 1470
    assert "ix_prediction_requests_requested_at" in {
        index["name"] for index in inspector.get_indexes("prediction_requests")
    }
    assert "ix_prediction_results_created_at" in {
        index["name"] for index in inspector.get_indexes("prediction_results")
    }
    assert "ix_api_audit_logs_created_at" in {
        index["name"] for index in inspector.get_indexes("api_audit_logs")
    }
    assert "ix_api_audit_logs_status_code" in {
        index["name"] for index in inspector.get_indexes("api_audit_logs")
    }


def test_postgresql_enforces_constraints_and_persists_audit_log() -> None:
    """Verifie FK, UNIQUE et audit log sur le moteur PostgreSQL cible."""
    response = client.post("/api/v1/predict", json=build_valid_payload(), headers=AUTH_HEADERS)

    assert response.status_code == 200

    with SessionLocal() as db:
        prediction_request = db.scalar(select(PredictionRequest))
        prediction_result = db.scalar(select(PredictionResult))
        audit_log = db.scalar(select(ApiAuditLog))

        assert prediction_request is not None
        assert prediction_result is not None
        assert audit_log is not None

        assert prediction_result.request_id == prediction_request.id
        assert audit_log.request_id == prediction_request.id
        assert audit_log.status_code == 200
        assert audit_log.endpoint == "/api/v1/predict"

        db.add(
            PredictionResult(
                request_id=prediction_request.id,
                prediction=prediction_result.prediction,
                score=prediction_result.score,
                threshold=prediction_result.threshold,
                model_version="duplicate-test",
                model_name=prediction_result.model_name,
            )
        )

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

        db.add(
            ApiAuditLog(
                request_id=999999,
                endpoint="/api/v1/predict",
                status_code=500,
                error_message="fk should fail",
            )
        )

        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
