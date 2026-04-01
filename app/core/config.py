"""Configuration centralisee de l'application.

Ce module utilise Pydantic Settings pour charger les variables
d'environnement de maniere typee. Le prefixe `P5_` evite d'absorber des
variables globales de la machine sans rapport avec le projet.

Le projet formalise trois environnements :
- `development` pour le travail local ;
- `test` pour la CI et Pytest ;
- `production` pour un deploiement distant.
"""

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Decrit les parametres de configuration attendus par l'application."""

    app_name: str = "Employee Attrition Prediction API"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool | None = None
    database_url: str | None = None
    api_key: str | None = None
    api_key_header_name: str = "X-API-Key"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="P5_",
        extra="ignore",
    )

    @model_validator(mode="after")
    def apply_environment_rules(self) -> "Settings":
        """Applique les valeurs par defaut et les garde-fous par environnement."""
        if self.debug is None:
            self.debug = self.environment == "development"

        if not self.database_url:
            if self.environment == "development":
                self.database_url = (
                    "postgresql+psycopg://postgres:postgres@127.0.0.1:5433/"
                    "p5_attrition"
                )
            elif self.environment == "test":
                self.database_url = "sqlite://"
            else:
                raise ValueError(
                    "P5_DATABASE_URL est obligatoire en environnement production."
                )

        if not self.api_key:
            if self.environment == "development":
                self.api_key = "p5-dev-local-key"
            elif self.environment == "test":
                self.api_key = "p5-test-key"
            else:
                raise ValueError(
                    "P5_API_KEY est obligatoire en environnement production."
                )

        return self


settings = Settings()
