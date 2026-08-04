"""
STARCORE Platform
Configuration Management
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "STARCORE Platform"
    app_version: str = "0.1.0-dev"

    # B104 suppressed: server must bind all interfaces in container (intentional)
    api_host: str = "0.0.0.0"  # nosec B104
    api_port: int = 8000

    debug: bool = False

    # False (default): human-readable text logs. True: one JSON object per
    # log line, suited for log aggregators (Loki, ELK, CloudWatch) that
    # expect structured input. See core/logger.py.
    log_json: bool = False

    database_url: str = "sqlite:///./data/starcore.db"

    api_key: str | None = None

    proxmox_host: str | None = None
    proxmox_user: str | None = None
    proxmox_token_name: str | None = None
    proxmox_token_value: str | None = None
    proxmox_verify_ssl: bool = True

    anthropic_api_key: str | None = None
    anthropic_model: str = "claude-sonnet-5"

    # AI provider selection — "anthropic" (default) or "openai-compatible"
    # (Ollama, LM Studio, vLLM, LocalAI, OpenAI, or any /v1/chat/completions server).
    ai_provider: str = "anthropic"
    # Required when ai_provider = "openai-compatible", e.g. http://localhost:11434/v1
    ai_base_url: str | None = None
    # Optional API key for the openai-compatible provider; many local servers don't need one.
    ai_api_key: str | None = None
    # Required when ai_provider = "openai-compatible", e.g. "llama3" (Ollama) or
    # "gpt-4o-mini" (OpenAI). There is no universal default: server-side model
    # catalogs differ, and falling back to an Anthropic model name here would
    # silently send a nonexistent model to the configured server.
    ai_model: str | None = None

    # Requests per minute allowed per client IP, applied globally to all
    # endpoints except /health (see core/main.py). 0 disables rate limiting
    # entirely -- useful for local development or trusted-network-only
    # deployments where an operator has already decided the exposure is
    # acceptable.
    rate_limit_per_minute: int = 60

    # OpenTelemetry OTLP/HTTP endpoint. When set, the OTel SDK is activated
    # and spans are exported to this collector (Jaeger, Grafana Tempo,
    # Honeycomb, etc.). When unset (the default), the no-op tracer is used
    # with zero overhead. See core/tracing.py.
    otlp_endpoint: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="STARCORE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
