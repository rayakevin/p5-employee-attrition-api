"""Tests d'integration du flux complet prediction + persistance."""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import ApiAuditLog, PredictionRequest, PredictionResult
from app.db.session import get_db
from app.main import app


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Injecte une base en memoire pour les tests d'integration."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


def build_valid_payload() -> dict:
    """Construit un payload metier complet pour le flux d'integration."""
    return {
        "age": 35,
        "genre": "Male",
        "revenu_mensuel": 4500,
        "statut_marital": "Married",
        "departement": "Research & Development",
        "poste": "Research Scientist",
        "nombre_experiences_precedentes": 3,
        "nombre_heures_travailless": 40,
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
        "heure_supplementaires": 1,
        "augementation_salaire_precedente": 12,
        "nombre_participation_pee": 1,
        "nb_formations_suivies": 3,
        "nombre_employee_sous_responsabilite": 0,
        "distance_domicile_travail": 12,
        "niveau_education": 3,
        "domaine_etude": "Life Sciences",
        "ayant_enfants": 1,
        "frequence_deplacement": "Travel_Rarely",
        "annees_depuis_la_derniere_promotion": 2,
        "annes_sous_responsable_actuel": 3,
    }


def reset_tracking_tables() -> None:
    """Vide les tables entre chaque test d'integration."""
    with TestingSessionLocal() as db:
        db.execute(delete(ApiAuditLog))
        db.execute(delete(PredictionResult))
        db.execute(delete(PredictionRequest))
        db.commit()


def set_test_db_override() -> None:
    """Force l'API a utiliser la base en memoire de ce module d'integration."""
    app.dependency_overrides[get_db] = override_get_db


def test_predict_persists_linked_request_result_and_audit_log() -> None:
    """Verifie le chainage complet requete -> resultat -> log technique."""
    set_test_db_override()
    reset_tracking_tables()

    response = client.post("/api/v1/predict", json=build_valid_payload())

    assert response.status_code == 200

    with TestingSessionLocal() as db:
        prediction_request = db.scalar(select(PredictionRequest))
        prediction_result = db.scalar(select(PredictionResult))
        audit_log = db.scalar(select(ApiAuditLog))

        assert prediction_request is not None
        assert prediction_result is not None
        assert audit_log is not None

        assert prediction_result.request_id == prediction_request.id
        assert audit_log.request_id == prediction_request.id
        assert prediction_result.prediction_request.id == prediction_request.id
        assert len(prediction_request.audit_logs) == 1
        assert prediction_request.audit_logs[0].status_code == 200
        assert prediction_request.prediction_result.model_name == prediction_result.model_name
        assert prediction_request.payload_json["departement"] == "Research & Development"


def test_predict_logs_technical_failure_without_result(monkeypatch) -> None:
    """Verifie qu'un echec technique cree un log 500 sans resultat metier."""
    set_test_db_override()
    reset_tracking_tables()

    def fail_prediction(_model_input):
        raise RuntimeError("modele indisponible")

    monkeypatch.setattr(
        "app.services.prediction_service.predict_attrition",
        fail_prediction,
    )

    response = client.post("/api/v1/predict", json=build_valid_payload())

    assert response.status_code == 500

    with TestingSessionLocal() as db:
        requests = db.scalars(select(PredictionRequest)).all()
        results = db.scalars(select(PredictionResult)).all()
        logs = db.scalars(select(ApiAuditLog)).all()

    assert len(requests) == 1
    assert results == []
    assert len(logs) == 1
    assert logs[0].request_id == requests[0].id
    assert logs[0].status_code == 500
    assert "modele indisponible" in (logs[0].error_message or "")
