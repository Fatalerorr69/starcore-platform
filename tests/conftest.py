"""
Pytest fixtures
"""

from __future__ import annotations

import pytest
from core.config import Settings, get_settings
from core.database import init_db


@pytest.fixture(autouse=True)
def _isolated_database(tmp_path):
    db_path = tmp_path / "test.db"
    init_db(Settings(database_url=f"sqlite:///{db_path}"))
    yield


@pytest.fixture(autouse=True)
def _api_key(monkeypatch):
    monkeypatch.setenv("STARCORE_API_KEY", "test-api-key")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _clean_event_bus():
    from core.events import event_bus

    event_bus._subscribers.clear()
    yield
    event_bus._subscribers.clear()


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset the process-wide rate limiter's in-memory counters between tests.

    `core.main.app` (and therefore `core.main.limiter`) is a single module-
    level singleton shared by every test file that does `from core.main
    import app`. Without this reset, request counts from an earlier test
    file would carry over into a later one via the limiter's shared
    in-memory storage, making pass/fail depend on total test-suite request
    volume and ordering rather than on each test's own behavior.
    """
    from core.main import limiter

    limiter.reset()
    yield
    limiter.reset()
