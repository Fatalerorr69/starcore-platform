"""
API Authentication Tests
"""

from core.config import get_settings
from core.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_protected_endpoint_requires_api_key_header():
    response = client.get("/providers")
    assert response.status_code == 401


def test_protected_endpoint_rejects_wrong_api_key():
    response = client.get("/providers", headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401


def test_protected_endpoint_accepts_correct_api_key():
    response = client.get("/providers", headers={"X-API-Key": "test-api-key"})
    assert response.status_code == 200


def test_health_endpoint_is_public():
    response = client.get("/health")
    assert response.status_code == 200


def test_root_endpoint_is_public():
    response = client.get("/")
    assert response.status_code == 200


def test_missing_server_key_configuration_returns_503(monkeypatch):
    monkeypatch.delenv("STARCORE_API_KEY", raising=False)
    get_settings.cache_clear()
    try:
        response = client.get("/providers", headers={"X-API-Key": "anything"})
        assert response.status_code == 503
    finally:
        get_settings.cache_clear()


# ---------------------------------------------------------------------------
# TD-11 regression tests: API key comparison must use hmac.compare_digest,
# not `!=`, to avoid a timing side-channel on the shared secret.
# ---------------------------------------------------------------------------


def test_protected_endpoint_rejects_key_of_different_length():
    """A key of a different length than the configured one must still be
    rejected. hmac.compare_digest() handles length mismatches safely; this
    test asserts observable behavior only, not the comparison mechanism,
    since timing itself isn't practically measurable in a unit test.
    """
    response = client.get("/providers", headers={"X-API-Key": "short"})
    assert response.status_code == 401


def test_protected_endpoint_rejects_key_matching_prefix_only():
    """A key that shares a long common prefix with the real key (but
    differs later) must be rejected. This is the specific shape of guess
    a timing attack would exploit against a naive `!=` comparison.
    """
    response = client.get("/providers", headers={"X-API-Key": "test-api-keyXXXX"})
    assert response.status_code == 401


def test_protected_endpoint_rejects_empty_key():
    response = client.get("/providers", headers={"X-API-Key": ""})
    assert response.status_code == 401
