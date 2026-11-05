import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "SmartLogistics AI"
    environment: str = "development"
    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "SmartLogistics AI"),
        environment=os.getenv("APP_ENV", "development"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )


settings = get_settings()