"""Tests unitaires de la logique de score du module predictor."""

import pandas as pd

from app.ml.predictor import compute_model_score


class DecisionFunctionModel:
    """Double de test exposant `decision_function`."""

    def decision_function(self, _model_input):
        return [0.42]


class PredictProbaModel:
    """Double de test exposant `predict_proba`."""

    def predict_proba(self, _model_input):
        return [[0.2, 0.8]]


class PredictOnlyModel:
    """Double de test exposant uniquement `predict`."""

    def predict(self, _model_input):
        return [1]


def test_compute_model_score_uses_decision_function_when_requested() -> None:
    """Utilise `decision_function` quand la metadata le demande."""
    model = DecisionFunctionModel()
    metadata = {"score_method": "decision_function"}
    model_input = pd.DataFrame([{"feature": 1.0}])

    score = compute_model_score(model, metadata, model_input)

    assert score == 0.42


def test_compute_model_score_uses_predict_proba_when_requested() -> None:
    """Utilise la probabilité positive quand `predict_proba` est demandé."""
    model = PredictProbaModel()
    metadata = {"score_method": "predict_proba"}
    model_input = pd.DataFrame([{"feature": 1.0}])

    score = compute_model_score(model, metadata, model_input)

    assert score == 0.8


def test_compute_model_score_falls_back_to_predict() -> None:
    """Bascule sur `predict` si aucune autre méthode n'est disponible."""
    model = PredictOnlyModel()
    metadata = {"score_method": "predict"}
    model_input = pd.DataFrame([{"feature": 1.0}])

    score = compute_model_score(model, metadata, model_input)

    assert score == 1.0
