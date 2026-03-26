from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="Employee Attrition Prediction API",
    version="0.1.0",
    description="API for employee attrition prediction"
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}