from __future__ import annotations

"""Orchestration métier de la prédiction.

Ce service fait le lien entre le payload métier reçu par l'API, la
construction des features attendues par le modèle et l'appel final à la
fonction de prédiction.
"""

from sqlalchemy.orm import Session

from app.db.models import ApiAuditLog, PredictionRequest, PredictionResult
from app.ml.predictor import predict_attrition
from app.ml.preprocess import build_model_features


def create_prediction_request(
    db: Session,
    payload: dict,
    source_channel: str = "api",
) -> PredictionRequest:
    """Enregistre le payload brut avant calcul de la prédiction.

    On persiste la requête en amont afin de conserver une trace même si le
    calcul du modèle échoue ensuite.
    """
    prediction_request = PredictionRequest(
        source_channel=source_channel,
        payload_json=payload,
    )
    db.add(prediction_request)
    db.commit()
    db.refresh(prediction_request)
    return prediction_request


def create_audit_log(
    db: Session,
    endpoint: str,
    status_code: int,
    request_id: int | None = None,
    error_message: str | None = None,
) -> ApiAuditLog:
    """Crée une trace technique liée à un appel API."""
    audit_log = ApiAuditLog(
        request_id=request_id,
        endpoint=endpoint,
        status_code=status_code,
        error_message=error_message,
    )
    db.add(audit_log)
    db.commit()
    db.refresh(audit_log)
    return audit_log


def create_prediction_result(
    db: Session,
    request_id: int,
    prediction_data: dict,
) -> PredictionResult:
    """Persiste la sortie du modèle pour une requête donnée."""
    prediction_result = PredictionResult(
        request_id=request_id,
        prediction=prediction_data["prediction"],
        score=prediction_data["score"],
        threshold=prediction_data["threshold"],
        model_version=prediction_data["model_version"],
        model_name=prediction_data["model_name"],
    )
    db.add(prediction_result)
    db.commit()
    db.refresh(prediction_result)
    return prediction_result


def get_prediction(
    payload: dict,
    db: Session,
    endpoint: str = "/api/v1/predict",
) -> dict:
    """Construit les features, appelle le modèle et persiste la traçabilité.

    La fonction enregistre :
    1. le payload reçu ;
    2. le résultat métier si la prédiction réussit ;
    3. un log technique de succès ou d'erreur.
    """
    prediction_request = create_prediction_request(db=db, payload=payload)

    try:
        model_input = build_model_features(payload)
        prediction_data = predict_attrition(model_input)
        create_prediction_result(
            db=db,
            request_id=prediction_request.id,
            prediction_data=prediction_data,
        )
        create_audit_log(
            db=db,
            request_id=prediction_request.id,
            endpoint=endpoint,
            status_code=200,
        )
        return prediction_data
    except ValueError as exc:
        db.rollback()
        create_audit_log(
            db=db,
            request_id=prediction_request.id,
            endpoint=endpoint,
            status_code=400,
            error_message=str(exc),
        )
        raise
    except Exception as exc:
        db.rollback()
        create_audit_log(
            db=db,
            request_id=prediction_request.id,
            endpoint=endpoint,
            status_code=500,
            error_message=str(exc),
        )
        raise
