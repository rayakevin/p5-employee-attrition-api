from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Employee Attrition Prediction API"
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()