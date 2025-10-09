from settings import Settings
from main import export_secrets


def test_settings_basic_fields_present():
    export_secrets()
    settings = Settings()

    assert hasattr(settings, "APP_NAME")
    assert hasattr(settings, "ENVIRONMENT")
    assert hasattr(settings, "EXAMPLE_API_KEY")

    assert isinstance(settings.APP_NAME, str) and settings.APP_NAME
    assert settings.ENVIRONMENT in {"dev", "test", "prod"}
    assert isinstance(settings.EXAMPLE_API_KEY, str) and settings.EXAMPLE_API_KEY
