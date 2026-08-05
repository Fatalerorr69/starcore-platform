# STARCORE Platform — Test Strategy

## Objective

The test suite must protect execution correctness, provider contracts, operational safety and release reproducibility. Code coverage is a quality signal, not the sole acceptance criterion.

## Test layers

### Unit tests

Cover pure logic and isolated components:

- blueprint models and validation;
- YAML loading and error reporting;
- dependency planning;
- cycle and unknown-dependency detection;
- task graph behavior;
- configuration validation;
- persistence repositories;
- provider action mapping.

### Property-based tests

Use Hypothesis for graph and planner invariants:

- every dependency precedes its dependent;
- every declared resource appears exactly once;
- unknown dependencies are rejected;
- cyclic graphs are rejected;
- independent nodes can share an execution wave;
- sequential and graph representations preserve dependency constraints.

### Integration tests

Exercise real application boundaries with isolated test resources:

- FastAPI routes with authentication;
- SQLite + Alembic migrations;
- CLI commands through Typer runner;
- provider registry integration;
- plugin discovery and registration;
- event emission and run history persistence.

### Provider contract tests

Every provider implementation must satisfy the same contract suite. Tests should verify:

- connect/disconnect lifecycle;
- repeated connect idempotency;
- concurrent connect safety;
- health behavior before and after connection;
- unsupported actions fail explicitly;
- provider failures do not leak secrets;
- list operations return stable normalized structures.

### Concurrency and stress tests

The scheduler must be tested with:

- multiple independent tasks using one provider;
- multiple providers in one execution;
- repeated concurrent connect calls;
- provider failure during a concurrent wave;
- cancellation during a running wave;
- exception in one task while siblings are running;
- large dependency graphs;
- repeated executions to expose lifecycle races.

### Failure-injection tests

Explicitly simulate:

- provider connection failure;
- provider timeout;
- provider execution exception;
- disconnect failure;
- unknown provider;
- invalid blueprint;
- database unavailable;
- migration mismatch;
- malformed provider response.

Tests must verify deterministic task status, cleanup, persistence and diagnostic output.

### Smoke tests

Required smoke paths:

- installed CLI starts;
- `starcore --help` succeeds;
- `starcore doctor --fast` succeeds;
- API starts;
- `/health` responds;
- authenticated endpoint rejects missing/invalid credentials;
- Docker image starts and passes healthcheck;
- package build succeeds;
- built wheel can be installed into a clean environment;
- installed CLI can execute a non-provider-dependent command.

### Security tests

Validate:

- secrets are not present in logs;
- API authentication is enforced where intended;
- dangerous provider operations require explicit confirmation where applicable;
- dependency and SAST scans run in CI;
- secret scanning runs in CI;
- Docker configuration does not accidentally expose scaffold services by default.

## Release acceptance

A release candidate is acceptable only when all of the following pass:

1. Ruff.
2. Pyright.
3. Full pytest suite.
4. Coverage threshold.
5. Hypothesis/property tests.
6. Integration tests.
7. Security scans.
8. Migration consistency check.
9. Package build and clean-install smoke test.
10. Docker build and `/health` smoke test.
11. Documentation build or link validation.

## Important principle

A 100% coverage result does not prove concurrency safety, correct failure propagation, idempotency or operational readiness. These dimensions require dedicated behavioral and integration tests.
