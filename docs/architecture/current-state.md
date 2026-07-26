# STARCORE Platform — Current Architecture

## Purpose

This document describes the currently implemented architecture. It is intentionally separate from the long-term vision in `docs/ses/`.

## Runtime layers

```text
CLI / FastAPI
      |
      v
Blueprint loading + validation
      |
      v
Execution Planner
      |
      +--> Sequential BlueprintExecutor
      |
      +--> TaskGraph -> Scheduler
                              |
                              v
                       Provider Registry
                         /          \
                        v            v
                    Docker        Proxmox
```

## Control surfaces

- `starcore blueprint plan`: validate and produce a dependency-aware plan.
- `starcore blueprint run`: execute a blueprint sequentially or with dependency-aware parallel scheduling.
- `starcore doctor`: local environment and readiness diagnostics.
- `starcore audit`: runtime/environment audit.
- `starcore diagnose`: deeper configuration, database and provider diagnostics.
- FastAPI exposes provider, blueprint, run-history, diagnostics and resource-action APIs.

## Execution semantics

The planner builds two representations from the same blueprint:

1. A flat dependency-ordered plan for sequential execution.
2. A `TaskGraph` for wave-based concurrent execution.

`depends_on` is a hard execution constraint. A task is eligible only after all declared dependencies have completed successfully from the scheduler's perspective.

## Provider lifecycle

Providers are registered in a process-wide registry and may be shared by concurrent tasks. Provider connection setup is guarded by a per-instance asynchronous connection lock. Docker and Proxmox providers use blocking SDK calls through `asyncio.to_thread`.

This design is concurrency-aware but remains a stabilization target: future work must verify provider operation safety, disconnect semantics, failure isolation, and idempotency under concurrent execution.

## Persistence

SQLite and SQLAlchemy provide run-history persistence. Alembic tracks schema migrations. CI verifies migration consistency with `alembic check`.

## Observability

- Structured logging via Loguru.
- Optional JSON logging through `STARCORE_LOG_JSON`.
- Prometheus-compatible `/metrics` endpoint.
- CLI/API diagnostics and environment detection.

## Security boundaries

The Docker provider requires access to the Docker socket. This is effectively host-root-equivalent authority and must be treated as a privileged deployment boundary. API authentication therefore protects a high-impact control plane and must not be considered sufficient isolation by itself.

## Known stabilization priorities

1. Verify scheduler failure propagation and dependency semantics with integration and property-based tests.
2. Verify concurrent provider operations and lifecycle behavior under stress.
3. Establish explicit provider contracts and capability metadata.
4. Add packaging/install smoke tests and release artifact validation.
5. Add Docker Compose configuration validation and runtime smoke coverage.
6. Keep current-state documentation synchronized with implementation changes.
