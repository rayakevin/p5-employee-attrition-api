"""Configuration centralisée de l'application.

Ce module utilise Pydantic Settings pour charger les variables
d'environnement de manière typée. Le préfixe `P5_` évite d'absorber des
variables globales de la machine sans rapport avec le projet.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Décrit les paramètres de configuration attendus par l'application."""

    app_name: str = "Employee Attrition Prediction API"
    environment: str = "development"
    debug: bool = True
    # SQLite est utilisé comme valeur locale non sensible pour démarrer vite.
    database_url: str = "sqlite:///./p5_attrition.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="P5_",
    )


settings = Settings()
