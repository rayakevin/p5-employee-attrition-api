from __future__ import annotations

"""Explication locale du score produit par le modele final.

Le modele final du projet est un pipeline scikit-learn compose d'un
`StandardScaler` suivi d'un `LinearSVC`. Pour un individu donne, la
`decision_function` peut donc etre decomposee en contributions additives
feature par feature :

score = intercept + somme(coef_i * feature_standardisee_i)

Cette decomposition constitue une explication locale fidele au comportement
du modele lineaire utilise en production.
"""

from typing import Any

import pandas as pd

from app.ml.loader import load_mlflow_model
from app.ml.preprocess import repair_common_mojibake


def prettify_feature_name(feature_name: str) -> str:
    """Rend un nom de feature technique plus lisible pour un utilisateur.

    Cette étape est importante car le modèle manipule des noms de colonnes
    orientés machine, alors que l'interface portfolio et la soutenance
    nécessitent des libellés métier plus compréhensibles.
    """
    repaired_name = repair_common_mojibake(feature_name)
    replacements = {
        "revenu_mensuel_log": "Revenu mensuel (log)",
        "annee_experience_totale_log": "Expérience totale (log)",
        "annees_dans_l_entreprise_log": "Ancienneté dans l'entreprise (log)",
        "annees_dans_le_poste_actuel_log": "Ancienneté dans le poste (log)",
        "annees_depuis_la_derniere_promotion_log": "Années depuis la dernière promotion (log)",
        "annes_sous_responsable_actuel_log": "Années sous le responsable actuel (log)",
        "distance_domicile_travail_classe": "Classe de distance domicile-travail",
        "ratio_anciennete_poste": "Ratio ancienneté poste / entreprise",
        "ratio_anciennete_manager": "Ratio ancienneté manager / entreprise",
        "ratio_experience_entreprise": "Ratio ancienneté entreprise / expérience",
        "mobilite_interne_potentielle": "Mobilité interne potentielle",
        "jamais_promu": "Jamais promu",
        "retard_promotion_relatif": "Retard de promotion relatif",
        "progression_salariale_faible": "Progression salariale faible",
        "mediane_revenu_par_niveau": "Médiane de revenu par niveau",
        "revenu_par_niveau": "Revenu rapporté au niveau hiérarchique",
        "sous_remunere_niveau": "Sous-rémunéré pour le niveau",
        "mediane_revenu_par_poste": "Médiane de revenu par poste",
        "revenu_par_poste": "Revenu rapporté au poste",
        "evolution_evaluation": "Évolution de l'évaluation",
        "bonne_perf_peu_augmente": "Bonne performance peu augmentée",
    }
    if repaired_name in replacements:
        return replacements[repaired_name]

    if repaired_name.startswith("statut_marital_"):
        return f"Statut marital : {repaired_name.removeprefix('statut_marital_')}"
    if repaired_name.startswith("departement_"):
        return f"Département : {repaired_name.removeprefix('departement_')}"
    if repaired_name.startswith("frequence_deplacement_"):
        return (
            "Fréquence de déplacement : "
            f"{repaired_name.removeprefix('frequence_deplacement_')}"
        )
    if repaired_name.startswith("poste_regroupe_"):
        return f"Poste regroupé : {repaired_name.removeprefix('poste_regroupe_')}"
    if repaired_name.startswith("domaine_etude_regroupe_"):
        return (
            "Domaine d'étude regroupé : "
            f"{repaired_name.removeprefix('domaine_etude_regroupe_')}"
        )

    return repaired_name.replace("_", " ").capitalize()


def _get_linear_components() -> tuple[Any, Any, dict]:
    """Recupere le pipeline, le classifieur lineaire final et la metadata."""
    model, metadata = load_mlflow_model()

    if not hasattr(model, "named_steps"):
        raise RuntimeError(
            "Le modele charge n'est pas un pipeline scikit-learn interpretable localement."
        )

    scaler = model.named_steps.get("scaler")
    linear_model = model.named_steps.get("model")

    if scaler is None or linear_model is None:
        raise RuntimeError(
            "Le pipeline attendu doit contenir un scaler et un estimateur final."
        )
    if not hasattr(linear_model, "coef_") or not hasattr(linear_model, "intercept_"):
        raise RuntimeError(
            "L'estimateur final ne fournit pas de coefficients exploitables pour "
            "l'explication locale."
        )

    return scaler, linear_model, metadata


def explain_prediction_locally(
    model_input: pd.DataFrame,
    top_n: int = 8,
) -> dict[str, Any]:
    """Retourne une decomposition locale du score du modele pour un individu.

    La fonction :
    1. standardise les features comme pendant l'entraînement ;
    2. applique les coefficients du modèle linéaire ;
    3. calcule les contributions individuelles ;
    4. renvoie les facteurs les plus positifs et les plus négatifs.
    """
    scaler, linear_model, metadata = _get_linear_components()

    scaled_input = scaler.transform(model_input)
    scaled_row = scaled_input[0]
    feature_names = list(model_input.columns)
    coefficients = linear_model.coef_[0]
    intercept = float(linear_model.intercept_[0])
    contributions = scaled_row * coefficients
    # Le score final du pipeline lineaire est la somme de l'intercept et des
    # contributions individuelles sur les variables standardisees.
    score = float(linear_model.decision_function(scaled_input)[0])

    rows: list[dict[str, Any]] = []
    for feature_name, feature_value, contribution in zip(
        feature_names, model_input.iloc[0].tolist(), contributions
    ):
        rows.append(
            {
                "feature": repair_common_mojibake(feature_name),
                "label": prettify_feature_name(feature_name),
                "value": float(feature_value),
                "contribution": float(contribution),
                "direction": "hausse" if float(contribution) >= 0 else "baisse",
            }
        )

    explanation_df = pd.DataFrame(rows).sort_values(
        "contribution", ascending=False
    ).reset_index(drop=True)

    top_positive = explanation_df.head(top_n).to_dict(orient="records")
    top_negative = (
        explanation_df.sort_values("contribution", ascending=True)
        .head(top_n)
        .to_dict(orient="records")
    )

    return {
        "model_name": metadata["model_name"],
        "model_version": metadata["model_version"],
        "score": score,
        "base_value": intercept,
        "positive_sum": float(explanation_df[explanation_df["contribution"] > 0]["contribution"].sum()),
        "negative_sum": float(explanation_df[explanation_df["contribution"] < 0]["contribution"].sum()),
        "top_positive": top_positive,
        "top_negative": top_negative,
    }
