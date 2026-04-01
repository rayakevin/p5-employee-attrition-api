"""Tests unitaires de la configuration applicative."""

import pytest

from app.core.config import Settings


def _clear_p5_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Supprime les variables P5_* qui pourraient biaiser le test."""
    for key in (
        "P5_ENVIRONMENT",
        "P5_DEBUG",
        "P5_DATABASE_URL",
        "P5_API_KEY",
        "P5_API_KEY_HEADER_NAME",
    ):
        monkeypatch.delenv(key, raising=False)


def test_settings_default_values_for_development(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifie les valeurs par defaut de l'environnement de developpement."""
    _clear_p5_env(monkeypatch)
    dev_settings = Settings(_env_file=None)

    assert dev_settings.app_name == "Employee Attrition Prediction API"
    assert dev_settings.environment == "development"
    assert dev_settings.debug is True
    assert dev_settings.api_key == "p5-dev-local-key"
    assert dev_settings.database_url.endswith("/p5_attrition")


def test_test_environment_sets_safe_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifie les valeurs dediees a l'environnement de test."""
    _clear_p5_env(monkeypatch)
    test_settings = Settings(environment="test", _env_file=None)

    assert test_settings.debug is False
    assert test_settings.api_key == "p5-test-key"
    assert test_settings.database_url == "sqlite://"


def test_production_requires_explicit_sensitive_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Refuse de demarrer en production sans secrets explicites."""
    _clear_p5_env(monkeypatch)
    with pytest.raises(ValueError):
        Settings(environment="production", _env_file=None)
