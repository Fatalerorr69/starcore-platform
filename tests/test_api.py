"""
Core API Tests
"""

from core.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_providers():
    response = client.get("/providers")
    assert response.status_code == 200
    names = [p["name"] for p in response.json()["providers"]]
    assert "docker" in names
    assert "proxmox" in names


def test_provider_health_unknown_returns_404():
    response = client.get("/providers/does-not-exist/health")
    assert response.status_code == 404


def test_provider_health_known_provider():
    response = client.get("/providers/docker/health")
    assert response.status_code == 200
    assert response.json()["provider"] == "docker"


def test_plan_blueprint():
    payload = {
        "name": "api-test",
        "version": "1.0",
        "resources": [{"name": "thing", "provider": "docker", "kind": "container", "config": {}}],
    }
    response = client.post("/blueprints/plan", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "api-test"
    assert len(body["steps"]) == 1


def test_run_blueprint_returns_task_results():
    payload = {
        "name": "api-run-test",
        "version": "1.0",
        "resources": [{"name": "thing", "provider": "docker", "kind": "container", "config": {}}],
    }
    response = client.post("/blueprints/run", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["tasks"][0]["status"] in ("failed", "skipped", "success")


def test_run_blueprint_parallel_query_param():
    payload = {
        "name": "api-parallel-test",
        "version": "1.0",
        "resources": [{"name": "thing", "provider": "docker", "kind": "container", "config": {}}],
    }
    response = client.post("/blueprints/run?parallel=true", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["tasks"][0]["status"] in ("failed", "skipped", "success")
