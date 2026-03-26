from fastapi import FastAPI

app = FastAPI(
    title="Employee Attrition Prediction API",
    version="0.1.0",
    description="API for employee attrition prediction, logging and deployment."
)


@app.get("/")
def root() -> dict:
    return {"message": "API is running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}