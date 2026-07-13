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
