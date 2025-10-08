# settings.py
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    ENVIRONMENT: str
    APP_NAME: str
    EXAMPLE_API_KEY: str

    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, value):
        #    ... # implement me!
        # prepare validator that will check whether the value of ENVIRONMENT is in (dev, test, prod)
        if value not in ("dev", "test", "prod"):
            raise ValueError("ENVIRONMENT not found in dev, test or prod")

        return value
