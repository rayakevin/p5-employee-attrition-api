from __future__ import annotations

from app.ml.predictor import predict_attrition
from app.ml.preprocess import build_model_features


def get_prediction(payload: dict) -> dict:
    model_input = build_model_features(payload)
    return predict_attrition(model_input)