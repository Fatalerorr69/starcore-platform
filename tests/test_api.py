"""
Core API Tests
"""

from unittest.mock import AsyncMock, patch

from blueprints.template_resolver import TemplateResolutionError
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


def test_list_runs_rejects_invalid_pagination_params():
    """TD-20: limit/offset are validated (limit 1..200, offset >= 0)."""
    assert client.get("/runs", params={"limit": 0}).status_code == 422
    assert client.get("/runs", params={"limit": 201}).status_code == 422
    assert client.get("/runs", params={"offset": -1}).status_code == 422
    assert client.get("/runs", params={"limit": 200, "offset": 0}).status_code == 200


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


def test_resource_action_endpoint_skips_unknown_provider():
    response = client.post(
        "/resources/action",
        json={"provider": "ghost", "action": "stop", "resource": "thing"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "skipped"


def test_provider_health_disconnects_when_connect_succeeds():
    """Line 181: disconnect() is called in the finally block when connect() returns True."""
    mock_provider = AsyncMock()
    mock_provider.connect.return_value = True
    mock_provider.health.return_value = {"status": "ok", "provider": "docker"}

    with (
        patch("core.main.registry.get", return_value=mock_provider),
        patch("core.main.registry.names", return_value=["docker"]),
    ):
        response = client.get("/providers/docker/health")

    assert response.status_code == 200
    mock_provider.disconnect.assert_awaited_once()


def test_resource_action_endpoint_passes_all_optional_fields():
    """Lines 220, 222, 224, 226: node/vmid/snapshot_name/description are forwarded in payload."""
    response = client.post(
        "/resources/action",
        json={
            "provider": "ghost",
            "action": "snapshot-create",
            "resource": "vm-101",
            "node": "pve",
            "vmid": 101,
            "snapshot_name": "snap-01",
            "description": "a test snapshot",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "skipped"


def test_generate_blueprint_endpoint_returns_parsed_blueprint():
    """Lines 271-273: valid YAML from generator is loaded into a Blueprint and returned."""
    valid_yaml = "name: gen-test\nversion: '1.0'\nresources: []\n"
    with patch("core.main.generate_blueprint_yaml", new=AsyncMock(return_value=valid_yaml)):
        response = client.post("/ai/generate-blueprint", json={"description": "a simple app"})
    assert response.status_code == 200
    body = response.json()
    assert body["yaml"] == valid_yaml
    assert body["blueprint"]["name"] == "gen-test"
    assert body["validation_error"] is None


def test_generate_blueprint_endpoint_returns_validation_error_for_bad_yaml():
    """Lines 274-275: YAML that fails Blueprint validation returns 200 with validation_error."""
    invalid_yaml = "not_a_blueprint: true\n"
    with patch("core.main.generate_blueprint_yaml", new=AsyncMock(return_value=invalid_yaml)):
        response = client.post("/ai/generate-blueprint", json={"description": "broken"})
    assert response.status_code == 200
    body = response.json()
    assert body["yaml"] == invalid_yaml
    assert body["validation_error"] is not None
    assert body["blueprint"] is None


def test_plan_blueprint_returns_422_on_template_resolution_error():
    """Lines 288-289: TemplateResolutionError from resolve_templates → HTTP 422."""
    payload = {
        "name": "tmpl-fail",
        "version": "1.0",
        "resources": [
            {"name": "vm", "provider": "proxmox", "kind": "vm", "config": {"template": "missing"}}
        ],
    }
    with patch(
        "core.main.resolve_templates",
        new=AsyncMock(side_effect=TemplateResolutionError("template not found")),
    ):
        response = client.post("/blueprints/plan", json=payload)
    assert response.status_code == 422
    assert "template not found" in response.json()["detail"]


def test_run_blueprint_returns_422_on_template_resolution_error():
    """Lines 321-322: TemplateResolutionError from resolve_templates → HTTP 422."""
    payload = {
        "name": "tmpl-fail-run",
        "version": "1.0",
        "resources": [
            {"name": "vm", "provider": "proxmox", "kind": "vm", "config": {"template": "missing"}}
        ],
    }
    with patch(
        "core.main.resolve_templates",
        new=AsyncMock(side_effect=TemplateResolutionError("template not found")),
    ):
        response = client.post("/blueprints/run", json=payload)
    assert response.status_code == 422
    assert "template not found" in response.json()["detail"]
