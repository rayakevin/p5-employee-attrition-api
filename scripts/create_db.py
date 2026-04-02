"""Script de création du schéma de base de données.

Ce script joue le rôle d'initialisation minimale du stockage applicatif.
Il peut être relancé sans logique métier complémentaire pour :

- charger la metadata SQLAlchemy du projet ;
- créer toutes les tables ORM déclarées ;
- préparer un environnement local ou conteneurisé avant seed et tests.
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
    """Crée physiquement les tables déclarées dans les modèles ORM.

    Le script s'appuie sur `Base.metadata.create_all(...)`, ce qui suffit
    dans le cadre pédagogique du projet où l'on ne gère pas encore de
    migrations versionnées avec Alembic.
    """
    Base.metadata.create_all(bind=engine)

    # `create_all()` ne rattrape pas toujours les nouveaux index quand les
    # tables existent deja. On les cree donc explicitement avec `checkfirst`
    # pour rendre le script plus idempotent lors des evolutions du schema.
    for table in Base.metadata.sorted_tables:
        for index in table.indexes:
            index.create(bind=engine, checkfirst=True)

    print("Database schema created successfully.")


if __name__ == "__main__":
    main()
