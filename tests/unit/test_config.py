from app.core.config import settings


def test_settings_default_values() -> None:
    assert settings.app_name == "Employee Attrition Prediction API"
    assert settings.environment == "development"
    assert settings.debug is True