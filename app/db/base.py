"""Base déclarative SQLAlchemy du projet.

Tous les modèles ORM héritent de cette classe afin de partager la même
metadata. Cette metadata est ensuite utilisée par `create_all` pour créer
le schéma de base.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe mère des modèles ORM SQLAlchemy."""

    pass
