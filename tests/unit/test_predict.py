"""Tests unitaires de l'endpoint de prediction."""

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
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Injecte une base en memoire pour isoler les tests de prediction."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def build_valid_payload() -> dict:
    """Construit un payload metier complet pour les cas nominaux."""
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


def reset_tracking_tables() -> None:
    """Vide les tables de traçabilité entre deux tests."""
    with TestingSessionLocal() as db:
        db.execute(delete(ApiAuditLog))
        db.execute(delete(PredictionResult))
        db.execute(delete(PredictionRequest))
        db.commit()


def set_test_db_override() -> None:
    """Force l'API a utiliser la base en memoire de ce module de test."""
    app.dependency_overrides[get_db] = override_get_db


def test_predict_valid() -> None:
    """Verifie qu'un payload valide renvoie une reponse 200 bien structuree."""
    set_test_db_override()
    reset_tracking_tables()
    payload = build_valid_payload()

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert "score" in data
    assert "threshold" in data
    assert "model_version" in data
    assert "model_name" in data

    assert isinstance(data["prediction"], int)
    assert isinstance(data["score"], float)
    assert isinstance(data["threshold"], float)

    with TestingSessionLocal() as db:
        requests = db.scalars(select(PredictionRequest)).all()
        results = db.scalars(select(PredictionResult)).all()
        logs = db.scalars(select(ApiAuditLog)).all()

    assert len(requests) == 1
    assert len(results) == 1
    assert len(logs) == 1
    assert logs[0].status_code == 200
    assert requests[0].payload_json["genre"] == "Homme"
    assert results[0].model_name == data["model_name"]


def test_predict_invalid_age() -> None:
    """Verifie qu'une valeur hors bornes est rejetee par la validation."""
    set_test_db_override()
    reset_tracking_tables()
    payload = build_valid_payload()
    payload["age"] = 10

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422

    with TestingSessionLocal() as db:
        requests = db.scalars(select(PredictionRequest)).all()
        results = db.scalars(select(PredictionResult)).all()
        logs = db.scalars(select(ApiAuditLog)).all()

    assert requests == []
    assert results == []
    assert logs == []
