from __future__ import annotations

"""Chargement de la metadata et du modèle MLflow.

Le rôle de ce module est de résoudre le bon chemin vers l'artefact MLflow
et de renvoyer à la fois le modèle chargé et sa metadata applicative.
"""

import json
from pathlib import Path

import mlflow.pyfunc

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts" / "model"
METADATA_PATH = ARTIFACTS_DIR / "metadata.json"


def load_model_metadata() -> dict:
    """Charge la metadata applicative associée au modèle exporté."""
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def resolve_model_path(model_uri: str) -> Path:
    """Résout un chemin de modèle robuste à partir de la metadata.

    On tente d'abord le chemin déclaré, puis des emplacements de repli
    cohérents avec les conventions d'export du projet.
    """
    model_path = Path(model_uri)
    if model_path.exists():
        return model_path

    for candidate in (ARTIFACTS_DIR, ARTIFACTS_DIR / "current"):
        if (candidate / "MLmodel").exists():
            return candidate

    raise FileNotFoundError(
        f"Le modele MLflow local est introuvable a l'emplacement : {model_uri}"
    )


def load_mlflow_model():
    """Charge le modèle MLflow et renvoie aussi sa metadata synchronisée."""
    metadata = load_model_metadata()
    model_path = resolve_model_path(metadata["mlflow_model_uri"])
    metadata["mlflow_model_uri"] = str(model_path.resolve())

    model = mlflow.pyfunc.load_model(str(model_path))
    return model, metadata
