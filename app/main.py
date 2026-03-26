"""Point d'entree principal de l'API FastAPI.

Ce module instancie l'application, branche le routeur versionne et expose
des endpoints simples de disponibilite. L'objectif est de garder ici un
code tres mince : la logique HTTP complexe reste dans les endpoints, et la
logique metier dans les services.
"""

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
    """Retourne un message simple pour verifier que l'application repond."""
    return {"message": "API is running"}


@app.get("/health")
def health():
    """Retourne un statut minimal de sante du service."""
    return {"status": "ok"}
