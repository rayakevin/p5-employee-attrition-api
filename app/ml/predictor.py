from __future__ import annotations

import pandas as pd

from app.ml.loader import load_mlflow_model

_MODEL = None
_MODEL_METADATA = None


def get_loaded_model():
    global _MODEL, _MODEL_METADATA

    if _MODEL is None or _MODEL_METADATA is None:
        _MODEL, _MODEL_METADATA = load_mlflow_model()

    return _MODEL, _MODEL_METADATA


def predict_attrition(model_input: pd.DataFrame) -> dict:
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