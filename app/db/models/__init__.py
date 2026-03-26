"""Exports centralisés des modèles ORM du projet.

L'import de ces modèles dans un point unique facilite la création du schéma
et évite d'oublier des tables lors du chargement de la metadata SQLAlchemy.
"""

from app.db.models.tracking import (
    ApiAuditLog,
    EmployeeSource,
    PredictionRequest,
    PredictionResult,
)

__all__ = [
    "ApiAuditLog",
    "EmployeeSource",
    "PredictionRequest",
    "PredictionResult",
]
