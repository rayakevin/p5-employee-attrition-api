"""Tests unitaires de la configuration applicative."""

from app.core.config import settings


def test_settings_default_values() -> None:
    """Verifie les valeurs par defaut de la configuration du projet."""
    assert settings.app_name == "Employee Attrition Prediction API"
    assert settings.environment == "development"
    assert settings.debug is True
