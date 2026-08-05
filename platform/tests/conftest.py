"""
Pytest fixtures
"""

from __future__ import annotations

import pytest
from core.config import Settings, get_settings
from core.database import init_db


@pytest.fixture(autouse=True)
def _no_dotenv_file(monkeypatch):
    """Prevent Settings() from ever reading a real .env file during tests.

    Settings.model_config declares env_file=".env", loaded relative to the
    process's current working directory. On a host where STARCORE has
    already been deployed (a populated .env with real Proxmox credentials
    and a real STARCORE_API_KEY sitting in the repo root), running the
    test suite from that directory would silently pick up production
    secrets -- tests written to assert "missing credentials" / "unset API
    key" behavior would instead observe real values and, in the Proxmox
    provider's case, make live network calls to production infrastructure
    instead of exercising the intended code path.

    Disabling env_file entirely (not just clearing individual OS env
    vars) makes every test's Settings() call depend only on explicit
    kwargs and monkeypatch.setenv/delenv, regardless of what happens to
    exist on disk in the working directory.
    """
    monkeypatch.setitem(Settings.model_config, "env_file", None)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def _isolated_database(tmp_path, _no_dotenv_file):
    db_path = tmp_path / "test.db"
    init_db(Settings(database_url=f"sqlite:///{db_path}"))
    yield


@pytest.fixture(autouse=True)
def _api_key(monkeypatch, _no_dotenv_file):
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
