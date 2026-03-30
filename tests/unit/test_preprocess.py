"""Tests unitaires du preprocessing d'inference."""

from __future__ import annotations

import pandas as pd

from app.ml.preprocess import build_model_features


def _build_payload_from_eda_employee(employee_id: int) -> dict:
    """Reconstruit un payload metier a partir d'un employe de reference."""
    df_eda = pd.read_csv("data/processed/df_EDA.csv")
    row = df_eda.loc[df_eda["id_employee"] == employee_id].iloc[0]
    return {
        "age": int(row["age"]),
        "genre": row["genre"],
        "revenu_mensuel": float(row["revenu_mensuel"]),
        "statut_marital": row["statut_marital"],
        "departement": row["departement"],
        "poste": row["poste"],
        "nombre_experiences_precedentes": int(row["nombre_experiences_precedentes"]),
        "annee_experience_totale": float(row["annee_experience_totale"]),
        "annees_dans_l_entreprise": float(row["annees_dans_l_entreprise"]),
        "annees_dans_le_poste_actuel": float(row["annees_dans_le_poste_actuel"]),
        "satisfaction_employee_environnement": int(row["satisfaction_employee_environnement"]),
        "note_evaluation_precedente": float(row["note_evaluation_precedente"]),
        "niveau_hierarchique_poste": int(row["niveau_hierarchique_poste"]),
        "satisfaction_employee_nature_travail": int(row["satisfaction_employee_nature_travail"]),
        "satisfaction_employee_equipe": int(row["satisfaction_employee_equipe"]),
        "satisfaction_employee_equilibre_pro_perso": int(row["satisfaction_employee_equilibre_pro_perso"]),
        "note_evaluation_actuelle": float(row["note_evaluation_actuelle"]),
        "heure_supplementaires": row["heure_supplementaires"],
        "augementation_salaire_precedente": float(row["augementation_salaire_precedente"]),
        "nombre_participation_pee": int(row["nombre_participation_pee"]),
        "nb_formations_suivies": int(row["nb_formations_suivies"]),
        "nombre_employee_sous_responsabilite": int(row["nombre_employee_sous_responsabilite"]),
        "distance_domicile_travail": float(row["distance_domicile_travail"]),
        "niveau_education": int(row["niveau_education"]),
        "domaine_etude": row["domaine_etude"],
        "frequence_deplacement": row["frequence_deplacement"],
        "annees_depuis_la_derniere_promotion": float(row["annees_depuis_la_derniere_promotion"]),
        "annes_sous_responsable_actuel": float(row["annes_sous_responsable_actuel"]),
    }


def test_build_model_features_matches_training_row_for_reference_employee() -> None:
    """Verifie qu'une ligne de reference retrouve les features du modele."""
    payload = _build_payload_from_eda_employee(554)
    inferred = build_model_features(payload)

    df_model = pd.read_csv("data/processed/df_MODEL.csv")
    expected = df_model.loc[df_model["id_employee"] == 554].drop(
        columns=["id_employee", "a_quitte_l_entreprise"]
    )

    pd.testing.assert_frame_equal(
        inferred.reset_index(drop=True),
        expected.reset_index(drop=True).astype(inferred.dtypes.to_dict()),
        check_exact=False,
        atol=1e-9,
        rtol=1e-9,
    )


def test_build_model_features_accepts_percentage_style_salary_input() -> None:
    """Accepte une saisie `12` tout en la convertissant vers `0.12`."""
    payload = _build_payload_from_eda_employee(554)
    payload["augementation_salaire_precedente"] = 16

    inferred = build_model_features(payload)

    assert float(inferred.iloc[0]["augementation_salaire_precedente"]) == 0.16
