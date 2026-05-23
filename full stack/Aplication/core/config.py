import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Professional E-Commerce API"
    app_env: str = "development"
    environment: str = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    database_url: str = "postgresql+psycopg://postgres:123456@localhost:5432/ecommerce_db"
    redis_url: str = "redis://localhost:6379/0"

    backend_cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )

    log_level: str = "INFO"
    log_json: bool = False

    @field_validator("environment", mode="before")
    @classmethod
    def default_environment_from_app_env(cls, value: Any) -> str:
        return str(value or "development")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return []

            if value.startswith("["):
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]

            return [item.strip() for item in value.split(",") if item.strip()]

        return ["http://localhost:5173", "http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    if settings.environment == "development" and settings.app_env:
        settings.environment = settings.app_env

    return settings