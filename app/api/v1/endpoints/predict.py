from __future__ import annotations

"""Endpoint HTTP de prédiction.

Ce module transforme un appel API en appel métier. Il valide l'entrée via
Pydantic, délègue la préparation des features et la prédiction au service,
puis reconstruit une réponse typée.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.prediction_service import get_prediction

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(
    data: PredictionInput,
    db: Session = Depends(get_db),
) -> PredictionOutput:
    """Exécute une prédiction unitaire à partir d'un payload métier.

    Étapes :
    1. Transformer le schéma Pydantic en dictionnaire natif.
    2. Déléguer le calcul au service métier.
    3. Revalider la sortie via `PredictionOutput`.
    4. Convertir les erreurs connues en erreurs HTTP adaptées.
    """
    try:
        result = get_prediction(data.model_dump(), db=db)
        return PredictionOutput(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de la prédiction : {exc}",
        ) from exc
