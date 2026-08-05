# STARCORE Platform — Claude Code Implementation Report (P2 cycle)

**Date:** 2026-07-26
**Branch:** `claude/p2-observability-hardening`
**Baseline commit:** `8713f79` (`main`, PR #89 merge)
**Source instruction:** P2 items explicitly deferred at the end of the P0+P1 cycle (`reports/STARCORE-Claude-Code-Handoff-2026-07-26.md` §5), executed on direct user instruction to continue.

---

## 1. Executive Summary

All four P2 items from the prior cycle's handoff were implemented and
validated this cycle: request correlation IDs, a snapshot-rollback
dry-run diff, a provider-concurrency-policy ADR (documenting a deliberate
no-limit decision, not adding a limit speculatively), and the README
status-table cleanup. The fifth, lowest-priority item (`docker compose
config`'s eager interpolation of an unused optional variable) was left
as-is, matching the prior cycle's own assessment that it doesn't affect
real usage and isn't worth the added complexity to fix.

**Net result:** 470 → 493 tests passing (+23), 100% coverage maintained
throughout, 0 lint/type errors at every commit, no architecture changes,
no breaking changes.

## 2. Baseline

| Gate | Result |
|---|---|
| `git status` at start | clean, `main` @ `8713f79` |
| `uv run pytest -q --cov --cov-fail-under=100` | 470 passed, 100% coverage |
| `uv run ruff check .` / `uv run pyright` | clean / 0 errors |

## 3. Implemented Changes

1. **`feat(observability): add request correlation IDs`** —
   `packages/core/main.py` gained `_request_id_middleware`: accepts a
   caller-supplied `X-Request-ID` if well-formed (alnum/hyphen/underscore,
   1–128 chars), generates a UUID4 otherwise, binds it to every log line
   via `logger.contextualize()` (`packages/core/logger.py` gained a
   default `request_id` extra field and a text-mode format that displays
   it), and echoes it back in the response header. Verified manually
   before writing tests that the binding is inherited by coroutines
   awaited from within the request (e.g. a `Scheduler.execute()` wave),
   with no extra propagation code, since `contextualize()` is
   `contextvars`-backed like `asyncio` itself.
2. **`feat(cli): add rollback dry-run diff before confirmation`** — new
   Proxmox provider action `snapshot-rollback-preview`
   (`packages/providers/proxmox/provider.py`) compares current config to
   the snapshot's config using only fields the Proxmox API actually
   returns for both; `config_diff` is explicitly `None` (not `{}`) when
   the API can't provide the snapshot's config, so the CLI never implies
   "no changes" when it simply couldn't check. `starcore snapshot
   rollback` (`apps/cli/main.py`) calls this before the existing
   `--yes`-skippable confirmation prompt.
3. **`docs(architecture): add ADR-013, provider concurrency policy`** —
   audited both providers' actual request path (`proxmoxer`'s
   `ProxmoxHttpSession` and `docker-py`'s `APIClient` both subclass
   `requests.Session`; verified STARCORE's token-based Proxmox auth
   doesn't mutate session state per-request). Decision: no concurrency
   limit added now — no evidence of a problem — with three concrete,
   stated trigger conditions for revisiting.
4. **`docs(readme): fix misleading "Planned, Not Built Yet" section`** —
   merged 9 already-`Done` rows into "What Works Today", kept only the 4
   genuinely-unstarted Vision items under a renamed section, added a
   short "Production Limitations" section pointing at the relevant ADRs
   instead of duplicating them.

## 4. Files Created

```
packages/core/security.py                        (from prior cycle, unaffected)
docs/adr/ADR-013-provider-concurrency-policy.md
tests/test_request_id.py
reports/STARCORE-Claude-Code-Implementation-Report-P2-2026-07-26.md  (this file)
```

## 5. Files Modified

```
packages/core/main.py           (+_request_id_middleware, _resolve_request_id)
packages/core/logger.py         (+request_id extra field, text-mode format)
packages/providers/proxmox/provider.py  (+_snapshot_rollback_preview)
apps/cli/main.py                (+_show_rollback_preview, wired into snapshot rollback)
docs/architecture.md            (correlation-ID pointer)
docs/api.md                     (Request correlation section)
docs/cli.md                     (snapshot rollback row updated)
docs/security.md                (ADR-013 cross-link)
mkdocs.yml                      (ADR-013 nav entry)
README.md                       (status table cleanup, test count)
tests/test_cli.py               (+9 snapshot-rollback-preview tests)
tests/test_providers.py         (+3 snapshot-rollback-preview provider tests)
```

## 6. Tests Added

23 net-new test functions (470 → 493):

| Area | Count | Highlights |
|---|---|---|
| Request correlation | 14 | `_resolve_request_id` edge cases, response header behavior (generated/echoed/replaced/distinct-per-request), two tests attaching a temporary loguru sink to prove `request_id` reaches log records during a request and reverts outside one |
| Rollback preview (provider) | 3 | Real diff, no-diff (configs match), diff unavailable (API error → `None`, not `{}`) |
| Rollback preview (CLI) | 9 | Diff shown, no-differences message, unavailable message, preview-failure graceful fallback, `--yes` skips the preview call entirely, confirming after a preview proceeds to the real rollback |

## 7. Quality Gates Executed (final state)

| Gate | Status | Result |
|---|---|---|
| `uv run ruff check .` | PASS | All checks passed |
| `uv run ruff format --check .` | PASS | 87 files formatted (1 file reformatted mid-cycle after a test edit, then re-verified) |
| `uv run pyright` | PASS | 0 errors, 0 warnings |
| `uv run pytest -q --cov --cov-fail-under=100` | PASS | 493 passed, 100.00% coverage |
| `uv run pip-audit` | PASS | No known vulnerabilities |
| `uv run bandit -r packages/ apps/ scripts/ -ll -q` | PASS | Clean |
| `uv lock --check` | PASS | No drift |
| `alembic upgrade head && alembic check` (throwaway DB) | PASS | No new upgrade operations detected |
| `uv run mkdocs build --strict` | PASS | Builds successfully |
| Docker build/run | NOT RE-RUN | No Dockerfile/docker-compose.yml changes this cycle (`git diff main..HEAD --stat` confirms); real CI's `docker-build` job still exercises the unchanged image on the PR |

## 8. Breaking Changes

None. Every change this cycle is additive: a new response header, a new
CLI confirmation step (opt-out via existing `--yes`), a new provider
action, a new ADR, documentation edits.

## 9. Remaining / Deferred

- `docker compose config`'s eager interpolation of `STARCORE_POSTGRES_PASSWORD`
  for the unused `scaffold` profile — still open, still assessed as
  cosmetic (doesn't affect `docker compose up -d --build api`, the
  actual documented workflow). Not fixed this cycle either; no new
  information changes that assessment.
- No other deferred work remains from the original runbook's P2 scope.
  Future work is genuinely new work, not a backlog item.
