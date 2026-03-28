from __future__ import annotations

"""Preparation des features avant l'appel au modele.

Ce module fait le pont entre le payload metier de l'API et le schema strict
attendu par le modele exporte dans MLflow. La logique principale consiste a :

1. normaliser les categories metier ;
2. recalculer les variables derivees utilisees a l'entrainement ;
3. reconstituer les colonnes one-hot ;
4. forcer les types finaux pour respecter la signature du modele.
"""

import json
import math
from pathlib import Path
import unicodedata

import pandas as pd

from app.ml.loader import load_model_metadata


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "model"
PREPROCESSING_REFERENCE_PATH = ARTIFACTS_DIR / "preprocessing_reference.json"

# Les valeurs conseillees cote API sont les libelles metier issus des CSV bruts.
# Certains alias anglais sont conserves pour ne pas casser les appels historiques.
GENRE_MAPPING = {
    "M": 1,
    "HOMME": 1,
    "MALE": 1,
    "F": 0,
    "FEMME": 0,
    "FEMALE": 0,
}

STATUT_MARITAL_MAPPING = {
    "CELIBATAIRE": "Célibataire",
    "SINGLE": "Célibataire",
    "MARIE(E)": "Marié(e)",
    "MARRIED": "Marié(e)",
    "DIVORCE(E)": "Divorcé(e)",
    "DIVORCED": "Divorcé(e)",
}

DEPARTEMENT_MAPPING = {
    "COMMERCIAL": "Commercial",
    "CONSULTING": "Consulting",
    "RESSOURCES HUMAINES": "Ressources Humaines",
    "SALES": "Commercial",
    "RESEARCH & DEVELOPMENT": "Consulting",
    "HUMAN RESOURCES": "Ressources Humaines",
}

FREQUENCE_DEPLACEMENT_MAPPING = {
    "AUCUN": "Aucun",
    "FREQUENT": "Frequent",
    "OCCASIONNEL": "Occasionnel",
    "NON-TRAVEL": "Aucun",
    "TRAVEL_FREQUENTLY": "Frequent",
    "TRAVEL_RARELY": "Occasionnel",
}

POSTE_MAPPING = {
    "ASSISTANT DE DIRECTION": "Assistant de Direction",
    "CADRE COMMERCIAL": "Cadre Commercial",
    "CONSULTANT": "Consultant",
    "DIRECTEUR TECHNIQUE": "Manager",
    "MANAGER": "Manager",
    "REPRESENTANT COMMERCIAL": "Cadre Commercial",
    "RESSOURCES HUMAINES": "Autre",
    "SENIOR MANAGER": "Senior Manager",
    "TECH LEAD": "Tech Lead",
    "SALES EXECUTIVE": "Cadre Commercial",
    "RESEARCH SCIENTIST": "Autre",
    "LABORATORY TECHNICIAN": "Tech Lead",
    "HUMAN RESOURCES": "Autre",
    "HEALTHCARE REPRESENTATIVE": "Autre",
    "MANUFACTURING DIRECTOR": "Manager",
    "SALES REPRESENTATIVE": "Cadre Commercial",
    "RESEARCH DIRECTOR": "Senior Manager",
}

DOMAINE_ETUDE_MAPPING = {
    "AUTRE": "Autre",
    "ENTREPREUNARIAT": "Entrepreunariat",
    "INFRA & CLOUD": "Infra & Cloud",
    "MARKETING": "Marketing",
    "RESSOURCES HUMAINES": "Autre",
    "TRANSFORMATION DIGITALE": "Transformation Digitale",
    "LIFE SCIENCES": "Autre",
    "MEDICAL": "Autre",
    "TECHNICAL DEGREE": "Infra & Cloud",
    "HUMAN RESOURCES": "Autre",
    "OTHER": "Autre",
}

BINARY_FLAG_MAPPING = {
    "OUI": 1,
    "NON": 0,
    "Y": 1,
    "YES": 1,
    "N": 0,
    "NO": 0,
    "TRUE": 1,
    "FALSE": 0,
    "1": 1,
    "0": 0,
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
    """Applique un log(1+x) securise en ramenant les valeurs negatives a 0."""
    return math.log1p(max(value, 0.0))


def safe_divide(numerator: float, denominator: float) -> float:
    """Retourne une division sure pour eviter une division par zero."""
    if denominator == 0:
        return 0.0
    return numerator / denominator


def repair_common_mojibake(value: str) -> str:
    """Tente de reparer un texte UTF-8 decode comme latin1.

    Le modele exporte contient des noms de colonnes avec accents mal encodes
    dans la metadata. Cette etape permet de rapprocher les libelles issus des
    CSV bruts des colonnes reelles du modele.
    """
    try:
        return value.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return value


def canonicalize_text(value: str) -> str:
    """Produit une cle de comparaison stable pour les libelles texte."""
    repaired = repair_common_mojibake(str(value)).strip()
    normalized = unicodedata.normalize("NFKD", repaired)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return without_accents.upper()


def load_preprocessing_reference() -> dict:
    """Charge les references de preprocessing calculees a l'entrainement.

    Si aucun fichier de reference n'existe encore, on renvoie une structure
    vide afin de garder une inference fonctionnelle avec des valeurs par
    defaut.
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
    """Ramene un poste metier vers une categorie connue du modele."""
    mapped_poste = poste_mapping.get(raw_poste, raw_poste)
    return POSTE_MAPPING.get(canonicalize_text(mapped_poste), mapped_poste)


def regroup_domaine_etude(raw_domain: str, domain_mapping: dict[str, str]) -> str:
    """Ramene un domaine d'etude vers une categorie connue du modele."""
    mapped_domain = domain_mapping.get(raw_domain, raw_domain)
    return DOMAINE_ETUDE_MAPPING.get(canonicalize_text(mapped_domain), mapped_domain)


def normalize_string_category(value: str, mapping: dict[str, str]) -> str:
    """Normalise une chaine metier selon un dictionnaire de correspondance."""
    cleaned_value = value.strip()
    return mapping.get(canonicalize_text(cleaned_value), cleaned_value)


def normalize_genre(value: str | int) -> int:
    """Convertit la representation metier du genre vers l'encodage du modele."""
    if isinstance(value, (int, float)):
        return int(value)

    normalized = GENRE_MAPPING.get(canonicalize_text(value))
    if normalized is None:
        raise ValueError(f"Genre non supporte pour la prediction: {value}")
    return normalized


def normalize_binary_flag(value: str | int | bool, field_name: str) -> int:
    """Normalise un indicateur binaire vers 0 ou 1."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        if int(value) in {0, 1}:
            return int(value)
        raise ValueError(f"Valeur binaire non supportee pour {field_name}: {value}")

    normalized = BINARY_FLAG_MAPPING.get(canonicalize_text(value))
    if normalized is None:
        raise ValueError(f"Valeur binaire non supportee pour {field_name}: {value}")
    return normalized


def resolve_expected_feature_name(
    expected_features: list[str], prefix: str, category: str
) -> str | None:
    """Retrouve le vrai nom de colonne du modele malgre les ecarts d'encodage."""
    expected_key = canonicalize_text(category)
    for feature in expected_features:
        if not feature.startswith(prefix):
            continue
        feature_label = feature.removeprefix(prefix)
        if canonicalize_text(feature_label) == expected_key:
            return feature
    return None


def compute_distance_class(distance: float) -> int:
    """Transforme la distance domicile-travail en classe ordinale simple."""
    if distance < 10:
        return 0
    if distance < 30:
        return 1
    return 2


def build_model_features(payload: dict) -> pd.DataFrame:
    """Construit le DataFrame final attendu par le modele exporte.

    Etapes principales :
    1. charger la metadata pour connaitre l'ordre des colonnes ;
    2. recharger les references de preprocessing si elles existent ;
    3. normaliser les categories du payload ;
    4. calculer les variables derivees ;
    5. preparer les colonnes one-hot ;
    6. forcer les types de sortie conformes au schema MLflow.
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
    domaine_etude_regroupe = regroup_domaine_etude(
        payload["domaine_etude"], domaine_mapping
    )

    # Si une categorie reconstituee n'existe pas dans le schema final, on
    # bascule vers "Autre" pour rester compatible avec le modele exporte.
    poste_col = resolve_expected_feature_name(
        expected_features, "poste_regroupe_", poste_regroupe
    )
    if poste_col is None:
        poste_regroupe = "Autre"
        poste_col = resolve_expected_feature_name(
            expected_features, "poste_regroupe_", poste_regroupe
        )

    domain_col = resolve_expected_feature_name(
        expected_features, "domaine_etude_regroupe_", domaine_etude_regroupe
    )
    if domain_col is None:
        domaine_etude_regroupe = "Autre"
        domain_col = resolve_expected_feature_name(
            expected_features, "domaine_etude_regroupe_", domaine_etude_regroupe
        )

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

    # Ce dictionnaire reconstruit d'abord les variables numeriques et derivees
    # avant l'ajout des colonnes one-hot.
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
        "heure_supplementaires": normalize_binary_flag(
            payload["heure_supplementaires"], "heure_supplementaires"
        ),
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
        "distance_domicile_travail_classe": compute_distance_class(
            payload["distance_domicile_travail"]
        ),
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

    # On initialise toutes les colonnes one-hot a 0 pour rester compatible
    # avec l'ordre et le schema du modele exporte.
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

    marital_col = resolve_expected_feature_name(
        expected_features, "statut_marital_", statut_marital
    )
    department_col = resolve_expected_feature_name(
        expected_features, "departement_", departement
    )
    travel_col = resolve_expected_feature_name(
        expected_features, "frequence_deplacement_", frequence_deplacement
    )

    if marital_col is not None:
        row[marital_col] = 1
    if department_col is not None:
        row[department_col] = 1
    if travel_col is not None:
        row[travel_col] = 1
    if poste_col is not None:
        row[poste_col] = 1
    if domain_col is not None:
        row[domain_col] = 1

    # Le DataFrame final respecte l'ordre exact attendu par le modele.
    final_row = {feature: row.get(feature, 0) for feature in expected_features}
    df = pd.DataFrame([final_row], columns=expected_features)

    # On force enfin les types reels du schema d'entree pour eviter les
    # erreurs de validation de schema cote MLflow.
    for feature in expected_features:
        if feature in INTEGER_FEATURES:
            df[feature] = df[feature].astype("int64")
        else:
            df[feature] = df[feature].astype("float64")

    return df
