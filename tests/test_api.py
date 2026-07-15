"""
Core API Tests
"""

from core.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
client.headers.update({"X-API-Key": "test-api-key"})


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


def test_run_blueprint_persists_and_is_retrievable():
    payload = {
        "name": "persist-test",
        "version": "1.0",
        "resources": [{"name": "thing", "provider": "docker", "kind": "container", "config": {}}],
    }
    run_response = client.post("/blueprints/run", json=payload)
    assert run_response.status_code == 200
    run_id = run_response.json()["run_id"]

    detail = client.get(f"/runs/{run_id}")
    assert detail.status_code == 200
    assert detail.json()["blueprint_name"] == "persist-test"


def test_get_run_detail_unknown_returns_404():
    response = client.get("/runs/does-not-exist")
    assert response.status_code == 404


def test_list_runs_returns_array():
    response = client.get("/runs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_plugins_endpoint_includes_example_plugin():
    response = client.get("/plugins")
    assert response.status_code == 200
    body = response.json()
    assert "example_provider" in body["discovered"]


def test_diagnostics_endpoint_returns_report():
    response = client.get("/diagnostics")
    assert response.status_code == 200
    body = response.json()
    assert "overall_status" in body
    assert "checks" in body


def test_dashboard_ui_serves_html():
    response = client.get("/ui")
    assert response.status_code == 200
    assert "STARCORE Dashboard" in response.text


def test_generate_blueprint_endpoint_returns_503_without_api_key():
    response = client.post("/ai/generate-blueprint", json={"description": "a simple web app"})
    assert response.status_code == 503


def test_proxmox_discover_endpoint_returns_connected_false_without_credentials():
    response = client.get("/proxmox/discover")
    assert response.status_code == 200
    assert response.json()["connected"] is False
