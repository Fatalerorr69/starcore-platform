# Sprint 022 — Property-Based Tests for Security, ADR-014

**Date:** 2026-07-26
**Branch:** `claude/new-session-s52x55`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A — Property-based tests for `core.security`

**`tests/test_property_based_security.py`** (6 tests):

| Test | Invariant |
|------|-----------|
| `test_redact_database_url_never_raises` | `redact_database_url` never raises for any string input |
| `test_redact_database_url_masks_postgres_password` | For any postgres DSN, `:{password}@` never appears in the output |
| `test_redact_database_url_sqlite_passthrough` | SQLite URLs carry no credentials; the rendered form always starts with `sqlite` |
| `test_scrub_configured_secrets_never_returns_configured_secret` | Output never contains the configured secret, for any `(text, secret)` pair |
| `test_scrub_configured_secrets_is_idempotent` | Calling scrub twice gives the same result as calling once |
| `test_scrub_configured_secrets_with_no_secrets_is_noop` | With no secrets configured, text is returned verbatim |

The Postgres password test initially asserted `password not in result`, which Hypothesis
falsified with `password='0'`, `hostname='000'` — `0` appears in the hostname portion
of the redacted URL. Corrected to `f":{password}@" not in result`, which targets only
the DSN password position.

### B — ADR-014: Task Timeout Integration — Deliberate Deferral

`orchestrator/timeout.py` (added in PR #100) is currently dead at runtime:
neither `Scheduler._run_task()` nor `BlueprintExecutor` call `execute_with_timeout`.
ADR-014 records this as a deliberate deferral — there is no correct global default
timeout for the full range of provider operations — and states three trigger conditions
for when to close the gap. This matches the pattern set by ADR-013 (concurrency
policy). `mkdocs.yml` nav updated to include ADR-014.

### C — Documentation update

- `docs/test-matrix.md`: "Secret redaction" row gains property-based checkmark,
  `test_property_based_security.py` added to its file list.
- `docs/changelog/sprint-022.md`: this file.
- `mkdocs.yml`: Sprint 022 nav entry added.
- `CHANGELOG.md`: [Unreleased] entry.

## Test counts

| Before | After |
|--------|-------|
| 548 passed | 554 passed |
| 100% coverage | 100% coverage |
