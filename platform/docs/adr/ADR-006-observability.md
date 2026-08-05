# ADR-006 — Observability: Prometheus Metrics & Structured Logging

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** Core team

---

## Context

STARCORE lacked runtime observability: no metrics, no structured log format compatible with
aggregation stacks (Loki, ELK). Debugging production issues required grepping plain-text logs.

## Decision

### Prometheus metrics endpoint (`GET /metrics`)

- Dedicated `CollectorRegistry` (not the global default) to avoid duplicate timeseries across
  test processes that import the module multiple times.
- Authenticated via `X-API-Key` — same shared-secret pattern as all other non-public endpoints.
- Three counters/histograms exposed:
  - `starcore_http_requests_total{method, path, status}` — request throughput per route.
  - `starcore_http_request_duration_seconds{method, path}` — latency histogram.
  - `starcore_blueprint_tasks_total{provider, status}` — task-level outcome telemetry.
- Middleware records metrics for every request; `/health` is included (unlike auth, rate-limiting).

### Structured logging via loguru

- `STARCORE_LOG_JSON=true` switches the loguru sink to `serialize=True` (JSON per line).
- Default is plain text for local development readability.
- The sink is configured at startup in both `core/main.py` and `apps/cli/main.py`; previously
  the `logger.py` configuration was defined but never imported.

## Consequences

**Positive**
- Prometheus scrape target is ready out-of-the-box; Grafana dashboards can be wired immediately.
- JSON logs can be shipped to Loki/ELK without a parsing step.
- No global registry pollution — test isolation is maintained.

**Negative / Trade-offs**
- One more authenticated endpoint to document for operators.
- `prometheus-client` added as a runtime dependency (~300 KB installed).
- Two startup call sites for logger configuration — must be kept in sync if a third entry point
  is ever added (e.g., a Celery worker).

## Alternatives considered

- **OpenTelemetry SDK**: more future-proof but significantly more complex to configure and
  would pull in a large dependency tree. Deferred until a tracing backend is chosen.
- **Structlog**: an alternative to loguru for structured output. Loguru was already in use;
  adding structlog would duplicate the logging layer.
