"""Script de création du schéma de base de données.

Ce script est pensé comme un point d'entrée simple à relancer en local.
Il charge la metadata SQLAlchemy puis crée toutes les tables déclarées.
"""

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# On ajoute explicitement la racine du projet pour que le script puisse
# être lancé depuis le terminal sans dépendre du répertoire courant.
from app.db.base import Base
from app.db.models import ApiAuditLog, EmployeeSource, PredictionRequest, PredictionResult
from app.db.session import engine


def main() -> None:
    """Crée physiquement les tables déclarées dans les modèles ORM."""
    Base.metadata.create_all(bind=engine)
    print("Database schema created successfully.")


if __name__ == "__main__":
    main()
