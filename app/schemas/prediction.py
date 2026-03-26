from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    age: int = Field(..., ge=18, le=65, description="Age of the employee")
    monthly_income: float = Field(..., gt=0, description="Monthly income")
    job_level: int = Field(..., ge=1, le=5, description="Job level")


class PredictionOutput(BaseModel):
    prediction: int
    probability: float