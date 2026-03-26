from app.ml.predictor import predict_attrition


def get_prediction(age: int, monthly_income: float, job_level: int) -> dict:
    prediction, probability = predict_attrition(age, monthly_income, job_level)

    return {
        "prediction": prediction,
        "probability": probability
    }