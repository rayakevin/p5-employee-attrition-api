from fastapi import FastAPI

app = FastAPI(
    title="Employee Attrition Prediction API",
    version="0.1.0",
    description="API for employee attrition prediction and prediction logging."
)


@app.get("/")
def root() -> dict:
    return {"message": "API is running"}