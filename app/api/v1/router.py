"""Agrégation des routes de l'API versionnée.

Ce module centralise l'enregistrement des endpoints de la version `v1`.
Il permet de faire évoluer l'API par version sans mélanger toutes les
routes dans `main.py`.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import predict

api_router = APIRouter()

# Chaque sous-route apporte sa propre responsabilité métier.
api_router.include_router(predict.router, tags=["Prediction"])
