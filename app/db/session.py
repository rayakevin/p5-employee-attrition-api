from __future__ import annotations

"""Gestion de l'engine et des sessions SQLAlchemy.

Ce module centralise la création de la connexion vers la base et fournit
une dépendance `get_db()` qui pourra être injectée plus tard dans FastAPI.
"""

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


def _prepare_sqlite_path(database_url: str) -> None:
    """Cree le dossier parent du fichier SQLite quand il est local.

    Sur certains runtimes conteneurises, un chemin SQLite peut exister dans
    la configuration sans que son dossier parent soit deja cree. SQLAlchemy
    ne cree pas ce dossier automatiquement, donc on le prepare ici avant
    l'ouverture de la connexion.
    """
    if not database_url.startswith("sqlite"):
        return

    url = make_url(database_url)
    if not url.database or url.database == ":memory:":
        return

    sqlite_path = Path(url.database)
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)


def _engine_kwargs(database_url: str) -> dict:
    """Retourne les paramètres d'engine adaptés au type de base utilisé.

    SQLite nécessite `check_same_thread=False` pour éviter des blocages
    fréquents dans des contextes applicatifs ou de tests. Les autres bases
    bénéficient de `pool_pre_ping=True` pour détecter les connexions mortes.
    """
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


_prepare_sqlite_path(settings.database_url)

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
