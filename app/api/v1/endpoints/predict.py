from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictionInput, PredictionOutput
from app.services.prediction_service import get_prediction

router = APIRouter()


@router.post("/predict", response_model=PredictionOutput)
def predict(data: PredictionInput) -> PredictionOutput:
    try:
        result = get_prediction(
            age=data.age,
            monthly_income=data.monthly_income,
            job_level=data.job_level
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))