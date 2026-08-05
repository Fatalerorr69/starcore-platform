# Sprint 021 — Property-Based Tests for Retry & Timeout, Stale Doc Update

**Date:** 2026-07-26
**Branch:** `claude/new-session-s52x55`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A — Property-based tests for `retry` and `timeout` modules

PR #100 added `provider_sdk.retry` and `orchestrator.timeout`; sprint-020 added unit
tests for both. Sprint-021 adds Hypothesis property-based tests to verify the
structural invariants that unit tests cannot exhaustively cover.

**`tests/test_property_based_retry.py`** (9 tests):

| Test | Invariant |
|------|-----------|
| `test_calculate_delay_always_within_bounds` | `calculate_delay()` always returns a value in `[0, max_delay]` for any combination of `base_delay`, `max_delay`, `exponential_base`, and `attempt` |
| `test_calculate_delay_no_jitter_is_deterministic` | With `jitter=False`, `calculate_delay()` returns the identical value on every call (no hidden randomness) |
| `test_calculate_delay_no_jitter_never_exceeds_max` | With `jitter=False`, result equals exactly `min(base × exp^attempt, max_delay)` |
| `test_calculate_delay_no_jitter_monotone_with_attempt` | With `jitter=False`, a higher attempt number always produces a delay ≥ a lower one |
| `test_retryable_error_message_attribute_matches` | `RetryableError.message` always equals the constructor argument |
| `test_retryable_error_last_exception_is_preserved` | `RetryableError.last_exception` is always the exact object passed in |
| `test_retryable_error_str_contains_message_and_cause` | `str(RetryableError)` always contains both the message and the cause's text |
| `test_attempt_with_retry_zero_retries_calls_operation_once` | `max_retries=0` means exactly one attempt, regardless of `operation_name` |
| `test_attempt_with_retry_non_retryable_always_propagates_immediately` | Non-retryable exceptions (not in `retryable_exceptions`) are always re-raised after exactly one call |

**`tests/test_property_based_timeout.py`** (8 tests):

| Test | Invariant |
|------|-----------|
| `test_timeout_config_is_enabled_for_any_positive_value` | `is_enabled()` is `True` for any `timeout_seconds > 0` |
| `test_timeout_config_is_disabled_for_non_positive` | `is_enabled()` is `False` for any `timeout_seconds <= 0` |
| `test_timeout_config_is_disabled_when_none` | `is_enabled()` is `False` when `timeout_seconds` is `None` |
| `test_timeout_config_never_raises_for_valid_inputs` | `TimeoutConfig` construction never raises for any valid `(float, TimeoutStrategy)` pair |
| `test_task_timeout_error_attributes_always_match_constructor` | `task_id`, `resource`, and `timeout` attributes always equal the constructor arguments |
| `test_task_timeout_error_str_contains_all_fields` | `str(TaskTimeoutError)` always contains `task_id` and `resource` |
| `test_task_timeout_error_is_exception` | `TaskTimeoutError` is always an `Exception` subclass and can be raised and caught |
| `test_execute_with_timeout_disabled_always_passes_through` | When `is_enabled()` is `False`, `execute_with_timeout` always returns the coroutine's result unchanged |

### B — Stale documentation update

`docs/test-matrix.md` had no rows for four modules added in sprints 019–020. Added:

| New row | Files |
|---------|-------|
| Retry logic (exponential backoff) | `test_retry.py`, `test_property_based_retry.py` |
| Task timeout | `test_timeout.py`, `test_property_based_timeout.py` |
| Request correlation | `test_correlation.py`, `test_request_id_middleware.py`, `test_request_id.py` |

`reports/starcore-tests-catalog.md` predated sprint-020 entirely (496 tests). Updated
to include all 6 new test files and 52 new test functions added in sprints 020–021.

## Test counts

| Before | After |
|--------|-------|
| 531 passed | 548 passed |
| 100% coverage | 100% coverage |
