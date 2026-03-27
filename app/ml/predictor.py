from __future__ import annotations

"""Prédiction métier à partir du modèle MLflow chargé.

Le modèle est mis en cache en mémoire pour éviter de le recharger à chaque
requête. Ce module reconstruit ensuite un dictionnaire de sortie exploitable
par l'API.
"""

import pandas as pd

from app.ml.loader import load_mlflow_model

_MODEL = None
_MODEL_METADATA = None


def get_loaded_model():
    """Charge le modèle une seule fois puis le réutilise en mémoire."""
    global _MODEL, _MODEL_METADATA

    if _MODEL is None or _MODEL_METADATA is None:
        _MODEL, _MODEL_METADATA = load_mlflow_model()

    return _MODEL, _MODEL_METADATA


def compute_model_score(model, metadata: dict, model_input: pd.DataFrame) -> float:
    """Calcule un score cohérent avec la méthode décrite dans la metadata.

    Cas gérés :
    - `decision_function` pour les modèles marginaux comme `LinearSVC`
    - `predict_proba` pour les modèles probabilistes
    - repli sur `predict` si aucune méthode de score dédiée n'est disponible
    """
    score_method = metadata.get("score_method", "predict")

    if score_method == "decision_function":
        if not hasattr(model, "decision_function"):
            raise RuntimeError(
                "Le modele charge ne supporte pas `decision_function` alors que "
                "la metadata l'exige. Le flavor MLflow charge est probablement incorrect."
            )
        raw_score = model.decision_function(model_input)
        return float(raw_score[0])

    if score_method == "predict_proba":
        if not hasattr(model, "predict_proba"):
            raise RuntimeError(
                "Le modele charge ne supporte pas `predict_proba` alors que "
                "la metadata l'exige."
            )
        raw_score = model.predict_proba(model_input)
        return float(raw_score[0][1])

    raw_score = model.predict(model_input)
    return float(raw_score[0])


def predict_attrition(model_input: pd.DataFrame) -> dict:
    """Produit une prédiction métier à partir des features préparées.

    Le modèle retourne ici un score brut. Ce score est comparé au seuil
    stocké dans la metadata afin de calculer la classe finale.
    """
    model, metadata = get_loaded_model()
    threshold = metadata["threshold"]

    score = compute_model_score(model, metadata, model_input)
    prediction = int(score >= threshold)

    return {
        "prediction": prediction,
        "score": score,
        "threshold": threshold,
        "model_version": metadata["model_version"],
        "model_name": metadata["model_name"],
    }
