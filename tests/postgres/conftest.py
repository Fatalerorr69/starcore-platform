"""
PostgreSQL smoke test fixtures.

Override the parent conftest's per-test SQLite isolation with PostgreSQL
session-level setup. All other autouse fixtures from the parent conftest
(api key, event bus, rate limiter) remain in effect.

Tests in this directory are skipped automatically when
STARCORE_TEST_POSTGRES_URL is not set.
"""

from __future__ import annotations

import os

import pytest
from core.config import Settings, get_settings
from core.database import Base, init_db
from provider_sdk.registry import registry
from sqlalchemy import text

_PG_URL = os.environ.get("STARCORE_TEST_POSTGRES_URL", "")


@pytest.fixture(scope="session", autouse=True)
def _pg_database():
    """Initialize PostgreSQL once for the entire smoke test session.

    Disables .env loading directly (monkeypatch is function-scoped so
    it cannot be used in a session fixture). The parent conftest's
    _no_dotenv_file fixture will also run per test, keeping things
    consistent.
    """
    if not _PG_URL:
        pytest.skip("STARCORE_TEST_POSTGRES_URL not set — skipping PostgreSQL smoke tests")

    original_env_file = Settings.model_config.get("env_file")
    Settings.model_config["env_file"] = None
    get_settings.cache_clear()

    init_db(Settings(database_url=_PG_URL))

    yield

    Settings.model_config["env_file"] = original_env_file
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _isolated_database(_pg_database):
    """Override parent: truncate all tables before each test.

    This gives function-level isolation without recreating the PostgreSQL
    schema on every test — schema setup happens once in _pg_database.
    """
    from core.database import _engine

    assert _engine is not None, "_pg_database must run before _isolated_database"
    with _engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DELETE FROM {table.name}"))  # noqa: S608
        conn.commit()
    yield


@pytest.fixture(autouse=True)
def _clear_provider_registry():
    """Clear provider registry between tests to avoid cross-test contamination."""
    registry._providers.clear()
    yield
    registry._providers.clear()
