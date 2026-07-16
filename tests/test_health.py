from fastapi.testclient import TestClient

from packages.core.config import get_settings
from packages.core.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# ---------------------------------------------------------------------------
# TD-16 regression tests: /health must reflect actual database reachability
# instead of returning an unconditional "healthy".
# ---------------------------------------------------------------------------


def test_health_reports_database_detail_on_success():
    response = client.get("/health")

    body = response.json()
    assert response.status_code == 200
    assert "database" in body
    assert "Connected" in body["database"]


def test_health_returns_503_when_database_is_unreachable(monkeypatch, tmp_path):
    # Point at a database URL whose parent directory cannot be created
    # (a file exists where a directory is expected), forcing the
    # connectivity check to fail deterministically without needing to
    # mock SQLAlchemy internals.
    blocked_path = tmp_path / "not-a-directory"
    blocked_path.write_text("this is a file, not a directory")
    bogus_db_path = blocked_path / "nested" / "starcore.db"

    monkeypatch.setenv("STARCORE_DATABASE_URL", f"sqlite:///{bogus_db_path}")
    get_settings.cache_clear()
    try:
        response = client.get("/health")
        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "unhealthy"
        assert "database" in body
    finally:
        get_settings.cache_clear()
