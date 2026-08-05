"""
Prometheus Metrics

Exposes application metrics for scraping at GET /metrics (see core/main.py).

HTTP request metrics are recorded by middleware. Blueprint task metrics are
recorded by subscribing to the process-wide EventBus's "task.completed"
event, so the orchestrator (packages/orchestrator/scheduler.py) and the
sequential executor (packages/blueprints/executor.py) stay unaware that
metrics collection exists -- both already emit that event for the plugin
system, and this module just adds another listener.

A dedicated CollectorRegistry is used instead of prometheus_client's global
default registry so this module can be imported multiple times across the
test suite without triggering "Duplicated timeseries" registration errors.
"""

from __future__ import annotations

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
)

from core.events import event_bus

registry = CollectorRegistry()

HTTP_REQUESTS_TOTAL = Counter(
    "starcore_http_requests_total",
    "Total HTTP requests handled, by method, route path, and status code",
    ["method", "path", "status"],
    registry=registry,
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "starcore_http_request_duration_seconds",
    "HTTP request duration in seconds, by method and route path",
    ["method", "path"],
    registry=registry,
)

BLUEPRINT_TASKS_TOTAL = Counter(
    "starcore_blueprint_tasks_total",
    "Total blueprint resource tasks executed, by provider and outcome",
    ["provider", "status"],
    registry=registry,
)


def record_task_completed(payload: dict) -> None:
    """EventBus subscriber for "task.completed". See scheduler.py / executor.py."""
    BLUEPRINT_TASKS_TOTAL.labels(
        provider=payload.get("provider", "unknown"),
        status=payload.get("status", "unknown"),
    ).inc()


event_bus.subscribe("task.completed", record_task_completed)


def render_metrics() -> bytes:
    """Render all registered metrics in Prometheus text exposition format."""
    return generate_latest(registry)
