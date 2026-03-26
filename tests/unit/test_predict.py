from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def build_valid_payload() -> dict:
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
        "annes_sous_responsable_actuel": 3
    }


def test_predict_valid() -> None:
    payload = build_valid_payload()

    response = client.post("/api/v1/predict", json=payload)

    print(response.status_code)
    print(response.json())

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


def test_predict_invalid_age() -> None:
    payload = build_valid_payload()
    payload["age"] = 10

    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 422