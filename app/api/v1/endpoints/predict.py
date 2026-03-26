from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.prediction_service import get_prediction

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput) -> PredictionOutput:
    try:
        result = get_prediction(data.model_dump())
        return PredictionOutput(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de la prédiction : {exc}",
        ) from exc