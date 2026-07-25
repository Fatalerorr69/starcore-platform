"""
Tests for core.metrics: Prometheus metrics collection and the /metrics endpoint.
"""

import pytest
from core.events import event_bus
from core.main import app
from core.metrics import BLUEPRINT_TASKS_TOTAL, record_task_completed, registry
from fastapi.testclient import TestClient

client = TestClient(app)
client.headers.update({"X-API-Key": "test-api-key"})


def _counter_value(name: str, labels: dict) -> float:
    return registry.get_sample_value(name, labels) or 0.0


def test_metrics_endpoint_requires_api_key():
    anon = TestClient(app)
    response = anon.get("/metrics")
    assert response.status_code == 401


def test_metrics_endpoint_returns_prometheus_text_format():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "starcore_http_requests_total" in response.text
    assert "starcore_blueprint_tasks_total" in response.text


def test_metrics_endpoint_records_the_request_that_fetched_it():
    before = _counter_value(
        "starcore_http_requests_total",
        {"method": "GET", "path": "/metrics", "status": "200"},
    )
    client.get("/metrics")
    after = _counter_value(
        "starcore_http_requests_total",
        {"method": "GET", "path": "/metrics", "status": "200"},
    )
    assert after == before + 1


def test_record_task_completed_increments_counter():
    before = _counter_value(
        "starcore_blueprint_tasks_total", {"provider": "docker", "status": "success"}
    )
    record_task_completed({"provider": "docker", "status": "success"})
    after = _counter_value(
        "starcore_blueprint_tasks_total", {"provider": "docker", "status": "success"}
    )
    assert after == before + 1


def test_record_task_completed_handles_missing_labels():
    record_task_completed({})
    value = _counter_value(
        "starcore_blueprint_tasks_total", {"provider": "unknown", "status": "unknown"}
    )
    assert value >= 1


@pytest.mark.asyncio
async def test_task_completed_event_updates_metrics():
    # The autouse `_clean_event_bus` fixture (tests/conftest.py) clears all
    # subscribers between tests for isolation from the plugin system, which
    # also wipes the module-level subscription core.metrics registers at
    # import time. Re-subscribe locally, same as test_blueprints.py and
    # test_scheduler.py do for their own "run.completed" listeners -- in
    # the real process this subscription is registered once and persists,
    # since nothing there clears it.
    event_bus.subscribe("task.completed", record_task_completed)

    before = _counter_value(
        "starcore_blueprint_tasks_total", {"provider": "proxmox", "status": "failed"}
    )
    await event_bus.emit(
        "task.completed", {"resource": "vm-1", "provider": "proxmox", "status": "failed"}
    )
    after = _counter_value(
        "starcore_blueprint_tasks_total", {"provider": "proxmox", "status": "failed"}
    )
    assert after == before + 1


def test_blueprint_tasks_total_metric_registered_before_first_use():
    # A direct sanity check that the metric object itself is wired to the
    # same registry rendered at /metrics -- catches accidental use of the
    # prometheus_client global default registry instead of core.metrics.registry.
    BLUEPRINT_TASKS_TOTAL.labels(provider="test-provider", status="success").inc()
    response = client.get("/metrics")
    assert 'provider="test-provider"' in response.text
