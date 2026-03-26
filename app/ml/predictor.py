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


def predict_attrition(model_input: pd.DataFrame) -> dict:
    """Produit une prédiction métier à partir des features préparées.

    Le modèle retourne ici un score brut. Ce score est comparé au seuil
    stocké dans la metadata afin de calculer la classe finale.
    """
    model, metadata = get_loaded_model()
    threshold = metadata["threshold"]

    raw_pred = model.predict(model_input)
    score = float(raw_pred[0])
    prediction = int(score >= threshold)

    return {
        "prediction": prediction,
        "score": score,
        "threshold": threshold,
        "model_version": metadata["model_version"],
        "model_name": metadata["model_name"],
    }
