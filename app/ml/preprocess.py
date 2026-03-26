from __future__ import annotations

import math
from pathlib import Path
import json

import pandas as pd

from app.ml.loader import load_model_metadata


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "model"
PREPROCESSING_REFERENCE_PATH = ARTIFACTS_DIR / "preprocessing_reference.json"

GENRE_MAPPING = {
    "M": 1,
    "MALE": 1,
    "HOMME": 1,
    "F": 0,
    "FEMALE": 0,
    "FEMME": 0,
}

STATUT_MARITAL_MAPPING = {
    "SINGLE": "Célibataire",
    "CELIBATAIRE": "Célibataire",
    "CÉLIBATAIRE": "Célibataire",
    "MARRIED": "Marié(e)",
    "MARIE(E)": "Marié(e)",
    "MARIÉ(E)": "Marié(e)",
    "DIVORCED": "Divorcé(e)",
    "DIVORCE(E)": "Divorcé(e)",
    "DIVORCÉ(E)": "Divorcé(e)",
}

DEPARTEMENT_MAPPING = {
    "SALES": "Commercial",
    "RESEARCH & DEVELOPMENT": "Consulting",
    "HUMAN RESOURCES": "Ressources Humaines",
}

FREQUENCE_DEPLACEMENT_MAPPING = {
    "NON-TRAVEL": "Aucun",
    "TRAVEL_FREQUENTLY": "Frequent",
    "TRAVEL_RARELY": "Occasionnel",
}

POSTE_MAPPING = {
    "SALES EXECUTIVE": "Cadre Commercial",
    "MANAGER": "Manager",
    "RESEARCH SCIENTIST": "Autre",
    "LABORATORY TECHNICIAN": "Tech Lead",
    "HUMAN RESOURCES": "Autre",
    "HEALTHCARE REPRESENTATIVE": "Autre",
    "MANUFACTURING DIRECTOR": "Manager",
    "SALES REPRESENTATIVE": "Cadre Commercial",
    "RESEARCH DIRECTOR": "Senior Manager",
}

DOMAINE_ETUDE_MAPPING = {
    "LIFE SCIENCES": "Autre",
    "MEDICAL": "Autre",
    "MARKETING": "Marketing",
    "TECHNICAL DEGREE": "Infra & Cloud",
    "HUMAN RESOURCES": "Autre",
    "OTHER": "Autre",
}

INTEGER_FEATURES = {
    "age",
    "genre",
    "nombre_experiences_precedentes",
    "satisfaction_employee_environnement",
    "note_evaluation_precedente",
    "niveau_hierarchique_poste",
    "satisfaction_employee_nature_travail",
    "satisfaction_employee_equipe",
    "satisfaction_employee_equilibre_pro_perso",
    "note_evaluation_actuelle",
    "heure_supplementaires",
    "nombre_participation_pee",
    "nb_formations_suivies",
    "distance_domicile_travail",
    "niveau_education",
    "distance_domicile_travail_classe",
    "mobilite_interne_potentielle",
    "jamais_promu",
    "progression_salariale_faible",
    "sous_remunere_niveau",
    "evolution_evaluation",
    "bonne_perf_peu_augmente",
}


def safe_log1p(value: float) -> float:
    return math.log1p(max(value, 0.0))


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def load_preprocessing_reference() -> dict:
    """
    Charge les statistiques et mappings issus du feature engineering entraînement.
    Si le fichier n'existe pas encore, on retourne des valeurs par défaut.
    """
    if PREPROCESSING_REFERENCE_PATH.exists():
        with open(PREPROCESSING_REFERENCE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {
        "poste_mapping": {},
        "domaine_etude_mapping": {},
        "mediane_revenu_par_niveau": {},
        "mediane_revenu_par_poste_regroupe": {},
    }


def regroup_poste(raw_poste: str, poste_mapping: dict[str, str]) -> str:
    mapped_poste = poste_mapping.get(raw_poste, raw_poste)
    return POSTE_MAPPING.get(mapped_poste.strip().upper(), mapped_poste)


def regroup_domaine_etude(raw_domain: str, domain_mapping: dict[str, str]) -> str:
    mapped_domain = domain_mapping.get(raw_domain, raw_domain)
    return DOMAINE_ETUDE_MAPPING.get(mapped_domain.strip().upper(), mapped_domain)


def normalize_string_category(value: str, mapping: dict[str, str]) -> str:
    return mapping.get(value.strip().upper(), value.strip())


def normalize_genre(value: str | int) -> int:
    if isinstance(value, (int, float)):
        return int(value)

    normalized = GENRE_MAPPING.get(value.strip().upper())
    if normalized is None:
        raise ValueError(f"Genre non supporte pour la prediction: {value}")
    return normalized


def compute_distance_class(distance: float) -> int:
    """
    Classe simple de distance.
    À ajuster si ton notebook utilise une logique différente.
    """
    if distance < 10:
        return 0
    if distance < 30:
        return 1
    return 2


def build_model_features(payload: dict) -> pd.DataFrame:
    """
    Transforme les données métier brutes en colonnes finales attendues par le modèle exporté.
    """
    metadata = load_model_metadata()
    expected_features: list[str] = metadata["feature_names"]

    refs = load_preprocessing_reference()
    poste_mapping = refs.get("poste_mapping", {})
    domaine_mapping = refs.get("domaine_etude_mapping", {})
    mediane_revenu_par_niveau = refs.get("mediane_revenu_par_niveau", {})
    mediane_revenu_par_poste_regroupe = refs.get("mediane_revenu_par_poste_regroupe", {})

    statut_marital = normalize_string_category(
        payload["statut_marital"], STATUT_MARITAL_MAPPING
    )
    departement = normalize_string_category(
        payload["departement"], DEPARTEMENT_MAPPING
    )
    frequence_deplacement = normalize_string_category(
        payload["frequence_deplacement"], FREQUENCE_DEPLACEMENT_MAPPING
    )
    poste_regroupe = regroup_poste(payload["poste"], poste_mapping)
    domaine_etude_regroupe = regroup_domaine_etude(payload["domaine_etude"], domaine_mapping)

    poste_col = f"poste_regroupe_{poste_regroupe}"
    if poste_col not in expected_features:
        poste_regroupe = "Autre"
        poste_col = f"poste_regroupe_{poste_regroupe}"

    domain_col = f"domaine_etude_regroupe_{domaine_etude_regroupe}"
    if domain_col not in expected_features:
        domaine_etude_regroupe = "Autre"
        domain_col = f"domaine_etude_regroupe_{domaine_etude_regroupe}"

    niveau_key = str(payload["niveau_hierarchique_poste"])
    mediane_niveau = float(
        mediane_revenu_par_niveau.get(niveau_key, payload["revenu_mensuel"])
    )
    mediane_poste = float(
        mediane_revenu_par_poste_regroupe.get(poste_regroupe, payload["revenu_mensuel"])
    )

    ratio_anciennete_poste = safe_divide(
        payload["annees_dans_le_poste_actuel"],
        payload["annees_dans_l_entreprise"],
    )
    ratio_anciennete_manager = safe_divide(
        payload["annes_sous_responsable_actuel"],
        payload["annees_dans_l_entreprise"],
    )
    ratio_experience_entreprise = safe_divide(
        payload["annees_dans_l_entreprise"],
        payload["annee_experience_totale"],
    )

    evolution_evaluation = (
        payload["note_evaluation_actuelle"] - payload["note_evaluation_precedente"]
    )

    jamais_promu = int(payload["annees_depuis_la_derniere_promotion"] == 0)
    progression_salariale_faible = int(payload["augementation_salaire_precedente"] < 10)
    bonne_perf_peu_augmente = int(
        payload["note_evaluation_actuelle"] >= 4
        and payload["augementation_salaire_precedente"] < 10
    )
    sous_remunere_niveau = int(payload["revenu_mensuel"] < mediane_niveau)
    mobilite_interne_potentielle = int(
        payload["annees_dans_le_poste_actuel"] >= 3
        and payload["annees_depuis_la_derniere_promotion"] >= 2
    )

    retard_promotion_relatif = safe_divide(
        payload["annees_depuis_la_derniere_promotion"],
        payload["annees_dans_l_entreprise"],
    )

    revenu_par_niveau = safe_divide(
        payload["revenu_mensuel"],
        max(payload["niveau_hierarchique_poste"], 1),
    )
    revenu_par_poste = safe_divide(
        payload["revenu_mensuel"],
        max(payload["nombre_employee_sous_responsabilite"] + 1, 1),
    )

    row: dict[str, float | int] = {
        "age": payload["age"],
        "genre": normalize_genre(payload["genre"]),
        "nombre_experiences_precedentes": payload["nombre_experiences_precedentes"],
        "satisfaction_employee_environnement": payload["satisfaction_employee_environnement"],
        "note_evaluation_precedente": payload["note_evaluation_precedente"],
        "niveau_hierarchique_poste": payload["niveau_hierarchique_poste"],
        "satisfaction_employee_nature_travail": payload["satisfaction_employee_nature_travail"],
        "satisfaction_employee_equipe": payload["satisfaction_employee_equipe"],
        "satisfaction_employee_equilibre_pro_perso": payload["satisfaction_employee_equilibre_pro_perso"],
        "note_evaluation_actuelle": payload["note_evaluation_actuelle"],
        "heure_supplementaires": payload["heure_supplementaires"],
        "augementation_salaire_precedente": payload["augementation_salaire_precedente"],
        "nombre_participation_pee": payload["nombre_participation_pee"],
        "nb_formations_suivies": payload["nb_formations_suivies"],
        "distance_domicile_travail": payload["distance_domicile_travail"],
        "niveau_education": payload["niveau_education"],
        "revenu_mensuel_log": safe_log1p(payload["revenu_mensuel"]),
        "annee_experience_totale_log": safe_log1p(payload["annee_experience_totale"]),
        "annees_dans_l_entreprise_log": safe_log1p(payload["annees_dans_l_entreprise"]),
        "annees_dans_le_poste_actuel_log": safe_log1p(payload["annees_dans_le_poste_actuel"]),
        "annees_depuis_la_derniere_promotion_log": safe_log1p(payload["annees_depuis_la_derniere_promotion"]),
        "annes_sous_responsable_actuel_log": safe_log1p(payload["annes_sous_responsable_actuel"]),
        "distance_domicile_travail_classe": compute_distance_class(payload["distance_domicile_travail"]),
        "ratio_anciennete_poste": ratio_anciennete_poste,
        "ratio_anciennete_manager": ratio_anciennete_manager,
        "ratio_experience_entreprise": ratio_experience_entreprise,
        "mobilite_interne_potentielle": mobilite_interne_potentielle,
        "jamais_promu": jamais_promu,
        "retard_promotion_relatif": retard_promotion_relatif,
        "progression_salariale_faible": progression_salariale_faible,
        "evolution_evaluation": evolution_evaluation,
        "bonne_perf_peu_augmente": bonne_perf_peu_augmente,
        "mediane_revenu_par_niveau": mediane_niveau,
        "revenu_par_niveau": revenu_par_niveau,
        "sous_remunere_niveau": sous_remunere_niveau,
        "mediane_revenu_par_poste": mediane_poste,
        "revenu_par_poste": revenu_par_poste,
    }

    # Colonnes one-hot : on initialise tout à 0 puis on active la bonne valeur si présente.
    for feature in expected_features:
        if feature.startswith("statut_marital_"):
            row.setdefault(feature, 0)
        elif feature.startswith("departement_"):
            row.setdefault(feature, 0)
        elif feature.startswith("frequence_deplacement_"):
            row.setdefault(feature, 0)
        elif feature.startswith("poste_regroupe_"):
            row.setdefault(feature, 0)
        elif feature.startswith("domaine_etude_regroupe_"):
            row.setdefault(feature, 0)

    marital_col = f"statut_marital_{statut_marital}"
    department_col = f"departement_{departement}"
    travel_col = f"frequence_deplacement_{frequence_deplacement}"

    if marital_col in expected_features:
        row[marital_col] = 1
    if department_col in expected_features:
        row[department_col] = 1
    if travel_col in expected_features:
        row[travel_col] = 1
    if poste_col in expected_features:
        row[poste_col] = 1
    if domain_col in expected_features:
        row[domain_col] = 1

    # On force le DataFrame dans l'ordre exact attendu par le modèle
    final_row = {feature: row.get(feature, 0) for feature in expected_features}

    df = pd.DataFrame([final_row], columns=expected_features)

    for feature in expected_features:
        if feature in INTEGER_FEATURES:
            df[feature] = df[feature].astype("int64")
        else:
            df[feature] = df[feature].astype("float64")

    return df
