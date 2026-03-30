from __future__ import annotations

"""Endpoints HTTP de prediction et d'explication locale.

Ce module expose :
- une route de prediction metier ;
- une route d'explication locale du score pour un individu.

Les deux routes reutilisent strictement le meme preprocessing, afin que
l'explication porte exactement sur les features finalement envoyeess au modele.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.prediction import (
    BatchPredictionInput,
    BatchPredictionOutput,
    PredictionExplanationOutput,
    PredictionInput,
    PredictionOutput,
)
from app.services.prediction_service import (
    get_batch_predictions,
    get_prediction,
    get_prediction_explanation,
)


router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(
    data: PredictionInput,
    db: Session = Depends(get_db),
) -> PredictionOutput:
    """Execute une prediction unitaire a partir d'un payload metier."""
    try:
        result = get_prediction(data.model_dump(), db=db)
        return PredictionOutput(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de la prediction : {exc}",
        ) from exc


@router.post("/predict/batch", response_model=BatchPredictionOutput)
def predict_batch(data: BatchPredictionInput) -> BatchPredictionOutput:
    """Execute un scoring batch sans persistance technique."""
    try:
        results = get_batch_predictions(
            [row.model_dump() for row in data.rows]
        )
        return BatchPredictionOutput(
            results=[PredictionOutput(**result) for result in results]
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors du batch : {exc}",
        ) from exc


@router.post("/explain", response_model=PredictionExplanationOutput)
def explain(data: PredictionInput) -> PredictionExplanationOutput:
    """Retourne une decomposition locale du score pour un individu."""
    try:
        result = get_prediction_explanation(data.model_dump())
        return PredictionExplanationOutput(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'explication : {exc}",
        ) from exc
