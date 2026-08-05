# Sprint 008 — .env.example LOG_JSON, Sprint-007 Changelog & Metrics Property Tests

**Date:** 2026-07-25
**Branch:** `claude/new-session-s73k91` → merged as PR #76
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A01 — `.env.example` doplnění `STARCORE_LOG_JSON`
`STARCORE_LOG_JSON` was added to `Settings` in sprint-006 but omitted from
`.env.example`. Added entry:

```
STARCORE_LOG_JSON=false
```

with a comment explaining the difference between plain-text and JSON log
output (Loki / ELK / CloudWatch use cases).

### B01 — `docs/changelog/sprint-007.md`
Created the missing changelog for sprint-007 (PR #75), covering:
- ruff PERF/N/FAST rule sets and all resulting fixes
- StarletteDeprecationWarning suppression via `filterwarnings`
- ADR-006 Observability

### C01 — Property-based tests for `core/metrics.py`
New `tests/test_property_based_metrics.py` — 6 Hypothesis property tests:

| Test | Invariant |
|------|-----------|
| `test_task_counter_increments_by_exactly_n` | Counter value equals n after n `.inc()` calls |
| `test_task_counter_labels_are_independent` | Different label sets don't interfere |
| `test_http_request_counter_increments_correctly` | HTTP counter tracks any method/path/status |
| `test_http_duration_histogram_count_matches_observations` | Histogram count == number of `.observe()` calls |
| `test_http_duration_histogram_sum_matches_total` | Histogram sum matches sum of observed values |
| `test_record_task_completed_tolerates_arbitrary_provider_and_status` | No exception for any string inputs |

## Test counts
| Before | After |
|--------|-------|
| 355 passed | 361 passed |
| 0 warnings | 0 warnings |
| 100% coverage | 100% coverage |
