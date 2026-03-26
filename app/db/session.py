from __future__ import annotations

"""Gestion de l'engine et des sessions SQLAlchemy.

Ce module centralise la création de la connexion vers la base et fournit
une dépendance `get_db()` qui pourra être injectée plus tard dans FastAPI.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _engine_kwargs(database_url: str) -> dict:
    """Retourne les paramètres d'engine adaptés au type de base utilisé.

    SQLite nécessite `check_same_thread=False` pour éviter des blocages
    fréquents dans des contextes applicatifs ou de tests. Les autres bases
    bénéficient de `pool_pre_ping=True` pour détecter les connexions mortes.
    """
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


engine = create_engine(
    settings.database_url,
    **_engine_kwargs(settings.database_url),
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """Ouvre une session SQLAlchemy puis la ferme proprement en fin d'usage."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
