"""
STARCORE Platform
Configuration Management
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "STARCORE Platform"
    app_version: str = "0.1.0-dev"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    debug: bool = False

    postgres_url: str = (
        "postgresql://starcore:starcore@localhost:5432/starcore"
    )

    redis_url: str = "redis://localhost:6379"

    nats_url: str = "nats://localhost:4222"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="STARCORE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
