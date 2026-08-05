# Sprint 020 — Post-Merge Repair, Coverage Restoration, Bug Fix

**Date:** 2026-07-26
**Branch:** `claude/new-session-s52x55`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Background

After PR #96 (sprint-019) merged, three external PRs (#98, #99, #100) landed on
`main` introducing new modules without tests and with a broken import that broke the
entire test suite at collection time. This sprint restores green CI.

## Changes

### A — Blocker: fix broken `provider_sdk` import and remove malformed workflow

`packages/provider_sdk/__init__.py` imported `ProviderException` — a name that does
not exist; the actual class in `exceptions.py` is `ProviderError`. This caused every
test in the suite to fail at collection time with an `ImportError`.

- Corrected the name to `ProviderError` and fixed the import order to satisfy ruff
  I001 (alphabetical: `RetryableError` before `RetryConfig`).
- Removed the unused `attempt_with_retry` import from `packages/provider_sdk/base.py`
  (ruff F401).
- Deleted `.github/workflows/main.yml`, which was a malformed YAML snippet (missing
  `on:` key, empty `path:` and `key:` fields) — not a real workflow.

### B — Tests for four untested modules from PR #100

PR #100 added four modules with 0% coverage. This bundle adds 35 new tests:

| Test file | Module under test | Tests added |
|-----------|-------------------|-------------|
| `tests/test_retry.py` | `provider_sdk.retry` — `RetryConfig`, `RetryableError`, `attempt_with_retry` | 11 |
| `tests/test_timeout.py` | `orchestrator.timeout` — `TimeoutConfig`, `TaskTimeoutError`, `execute_with_timeout` | 12 |
| `tests/test_correlation.py` | `core.correlation` — `set_request_id`, `get_request_id`, `resolve_request_id`, `contextualize_request` | 9 |
| `tests/test_request_id_middleware.py` | `core.request_id_middleware` — `RequestIdMiddleware` | 3 |

Timeout tests monkeypatch `asyncio.wait_for` to exercise all branches (CANCEL,
WAIT_AND_MARK success/double-timeout, IGNORE, unknown strategy) without real sleep
delays. A `_FakeStrategy` sentinel triggers the defensive `else` branch.

### C — Ruff and pyright violations in PR #100 modules

Five modules introduced by PR #100 had lint/type violations that caused ruff and
pyright CI gates to fail:

| File | Violations fixed |
|------|-----------------|
| `packages/provider_sdk/retry.py` | UP035 (`typing` → `collections.abc`), UP047 (PEP 695 type params), F841 (unused `last_exception`), added `# pragma: no cover` on the unreachable post-loop `raise` |
| `packages/orchestrator/timeout.py` | UP042 (`str, Enum` → `StrEnum`), E501 (line too long), UP041×2 (`asyncio.TimeoutError` → builtin `TimeoutError`), B904 (bare `raise` in `except` without `from`) |
| `packages/core/correlation.py` | UP045 (`Optional[str]` → `str | None`) |
| `packages/provider_sdk/__init__.py` | I001 (import order) |
| `tests/test_*.py` (4 files) | I001 (import order) |

Pyright reported `float | None` where `float` was expected in `timeout.py`'s
`execute_with_timeout`. Extracted `config.timeout_seconds` to a narrowed local
`timeout: float` immediately after the `is_enabled()` guard to satisfy the type
checker without suppressing the check.

### D — Bug fix: `classify_client_platform` marker priority

A Hypothesis property test (`test_classify_client_platform_any_string_containing_script_marker_is_script`)
found that `core.environment.classify_client_platform` returned `"browser-desktop"` for
any UA containing both a script marker (e.g. `curl`) and a browser marker (e.g.
`chrome`) because browser markers were checked first. Swapped the order so script
markers are checked before browser markers — script tokens are both more specific and
more intentional than browser name substrings.

## Test counts

| Before | After |
|--------|-------|
| 0 passed (ImportError at collection) | 531 passed |
| — | 100% coverage |
