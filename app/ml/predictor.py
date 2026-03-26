def predict_attrition(age: int, monthly_income: float, job_level: int) -> tuple[int, float]:
    """
    Fake prediction function (to be replaced by real ML model).
    """
    # logique simple pour le moment
    score = (monthly_income / 1000) + job_level - (age / 50)

    probability = min(max(score / 10, 0), 1)

    prediction = 1 if probability > 0.5 else 0

    return prediction, probability