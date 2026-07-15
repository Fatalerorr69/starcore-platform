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

    postgres_url: str = "postgresql://starcore:starcore@localhost:5432/starcore"

    redis_url: str = "redis://localhost:6379"

    nats_url: str = "nats://localhost:4222"

    database_url: str = "sqlite:///./data/starcore.db"

    api_key: str | None = None

    proxmox_host: str | None = None
    proxmox_user: str | None = None
    proxmox_token_name: str | None = None
    proxmox_token_value: str | None = None
    proxmox_verify_ssl: bool = True

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="STARCORE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
