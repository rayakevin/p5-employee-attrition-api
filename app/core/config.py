from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Employee Attrition Prediction API"
    environment: str = "development"
    debug: bool = True

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()