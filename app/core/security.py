"""Mecanismes simples d'authentification pour l'API.

Le projet reste dans un cadre pedagogique, donc le besoin n'est pas de
mettre en place une IAM complete, mais de montrer un controle d'acces
fonctionnel, documente et testable. Le choix retenu est une cle d'API
transmise dans un en-tete HTTP.
"""

from __future__ import annotations

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings


api_key_header = APIKeyHeader(
    name=settings.api_key_header_name,
    auto_error=False,
    description=(
        "Cle d'API requise pour acceder aux routes de prediction, "
        "d'explication et de batch."
    ),
)


def require_api_key(api_key: str | None = Security(api_key_header)) -> str:
    """Verifie la presence d'une cle d'API valide.

    Les endpoints techniques publics comme `/` et `/health` restent ouverts.
    Les routes metier sont protegees afin de montrer une premiere couche
    simple de controle d'acces conforme au cahier des charges du projet.
    """
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cle d'API absente ou invalide.",
        )
    return api_key


def build_api_auth_headers() -> dict[str, str]:
    """Construit les en-tetes d'authentification a reutiliser cote client."""
    return {settings.api_key_header_name: settings.api_key}
