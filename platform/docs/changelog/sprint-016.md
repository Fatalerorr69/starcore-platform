# Sprint 016 — Evidence-Based Audit: Vendor Lock-In Fix, DB URL Redaction, Failure-Propagation Regression Tests

_Renumbered from "Sprint 015" to "Sprint 016" during PR review: this work was branched before PR #86 (also titled "Sprint 015", merged separately to `main`) landed, so both claimed the same sprint number independently. Content below is otherwise unchanged from what actually ran._

**Date:** 2026-07-26
**Branch:** `claude/vstupni-prompt-report-czz7il`
**Mode:** Full technical audit (inventory → architecture review → risk review → targeted stabilization → validation → report), per the STARCORE Master Prompt v1.0.

## Starting point

All CI gates were already green before this sprint: `ruff check .`, `pyright`
(0 errors), `pytest -q --cov --cov-fail-under=100` (442 passed, 100%
coverage), `pip-audit` (no known vulnerabilities), `bandit -r packages/ apps/
scripts/ -ll -q` (clean), `uv lock --check`, and `alembic upgrade head &&
alembic check` against a throwaway database (no drift). This sprint's job was
to find what a green CI board doesn't catch — semantic/behavioral gaps,
config bugs, and unauthenticated info-disclosure surfaces — not to reopen
already-closed risks (RISK-01 provider concurrency and RISK-02 dependency
ordering, both closed in ADR-001/ADR-002, were re-verified by direct code
read and left untouched).

## Changes

### Fixed: `openai-compatible` AI provider silently sent an Anthropic model name (vendor lock-in bug)
`packages/ai/generator.py`'s `_build_provider()` passed
`settings.anthropic_model` (default `"claude-sonnet-5"`) as the `model` field
for the `openai-compatible` branch too. A user who configured
`STARCORE_AI_PROVIDER=openai-compatible` and `STARCORE_AI_BASE_URL` for
Ollama/LM Studio/vLLM/LocalAI, without *also* overriding
`STARCORE_ANTHROPIC_MODEL`, would silently send `model: "claude-sonnet-5"` to
their local server and get a model-not-found error — the exact vendor
coupling ADR-007 states the abstraction eliminates. `tests/test_ai_generator.py`
only asserted `isinstance(provider, OpenAICompatProvider)`, never the model
value, so 100% coverage did not catch it.

Fix: added an independent `STARCORE_AI_MODEL` setting
(`packages/core/config.py`), required (like `STARCORE_AI_BASE_URL`) for the
`openai-compatible` provider with no fallback — there is no universal
default model name across local-LLM servers, and falling back to an
Anthropic model name is exactly the bug being fixed. `.env.example`,
`README.md`, and `docs/installation.md` updated to document it.

### Fixed: unauthenticated `GET /health` echoed the raw `STARCORE_DATABASE_URL`, including embedded credentials
`check_database_connectivity()` (`packages/core/diagnostics.py`) returned
`f"Connected to {settings.database_url}"` verbatim, and this detail string is
surfaced by the **public, unauthenticated** `/health` endpoint (by design, so
container orchestrators can probe it without a credential). The default
SQLite URL carries no secret, but `STARCORE_DATABASE_URL` is documented as
freely configurable (e.g. Postgres), and a DSN of the form
`postgresql://user:password@host/db` would have been disclosed to any
unauthenticated caller. This violates the platform's own security invariant
("health/diagnostics endpoints must not disclose sensitive data without
authorization") and was not caught by any existing test.

Fix: added `_redact_database_url()`, using SQLAlchemy's
`URL.render_as_string(hide_password=True)` to mask credentials before they
reach either `/health` or `/diagnostics`; falls back to a fixed placeholder
(never the raw input) if the URL can't be parsed. No behavior change for the
default SQLite URL, which has no credentials to mask.

### New regression tests: dependent tasks are still attempted after a declared dependency fails
Neither `BlueprintExecutor` (sequential) nor `Scheduler` (parallel) checks
whether a resource's `depends_on` prerequisite actually *succeeded* before
attempting the dependent — both only gate on the prerequisite having
*finished* (`scheduler.py`'s `completed` set, `executor.py`'s unconditional
plan iteration). This is consistent between the two execution paths (no
divergence bug) and is unchanged by this sprint, but it was previously
unverified by any test and undocumented outside the source itself — a
regression could have silently flipped this behavior either way. Added one
test per execution path
(`test_executor_still_attempts_dependent_after_dependency_fails`,
`test_scheduler_still_attempts_dependent_after_dependency_fails`) that locks
in and documents the current, verified behavior. See the audit report's risk
matrix (RISK-05) for the open product question this raises (should a
dependent be skipped when its dependency fails?) — deliberately left as a
recommendation, not a unilateral semantics change, since it's a product
decision, not a bug.

### Fixed: stale README claim about `create_all()` behavior
`README.md`'s "What's Planned, Not Built Yet" table described pre-ADR-005
behavior ("create_all() still runs on app start for dev convenience"). Actual
behavior (`packages/core/database.py`, ADR-005): `create_all()` runs exactly
once, only on a genuinely fresh/untracked database, and the app fails fast on
startup if an existing database's revision doesn't match the migration head.
Corrected; test count in the same table updated 442 → 447.

## New tests (5)

| Test | File | Protects against |
|---|---|---|
| `test_build_provider_raises_without_ai_model` | `test_ai_generator.py` | Missing `STARCORE_AI_MODEL` silently falling back instead of failing loudly |
| `test_build_provider_returns_openai_compat_provider` (extended) | `test_ai_generator.py` | Regression of the vendor lock-in fix — asserts `provider._model == "llama3"`, not just `isinstance` |
| `test_redact_database_url_falls_back_on_unparseable_url` | `test_diagnostics.py` | Unparseable DSN ever reaching a response body raw |
| `test_check_database_connectivity_redacts_credentials_in_database_url` | `test_diagnostics.py` | Credential leakage regression in the shared `/health` + `/diagnostics` detail message |
| `test_executor_still_attempts_dependent_after_dependency_fails` | `test_blueprints.py` | Silent, undocumented change to failure-propagation semantics (sequential path) |
| `test_scheduler_still_attempts_dependent_after_dependency_fails` | `test_scheduler.py` | Same, concurrent path |

(Table lists 6 rows because one existing test was extended in place rather
than duplicated; net new test functions: 5, 442 → 447.)

## Validations run

- `uv sync --extra dev` — clean
- `uv run ruff check .` — all checks passed (before and after changes)
- `uv run pyright` — 0 errors, 0 warnings (before and after changes)
- `uv run pytest -q --cov --cov-report=term-missing --cov-fail-under=100` — 447 passed, 100% coverage
- `uv run pip-audit` — no known vulnerabilities
- `uv run bandit -r packages/ apps/ scripts/ -ll -q` — clean
- `uv lock --check` — resolved, no drift
- `alembic upgrade head && alembic check` against a throwaway SQLite database — no new upgrade operations detected

## Test counts

| Before | After |
|--------|-------|
| 442 passed | 447 passed |
| 100% coverage | 100% coverage |
| 0 pyright errors | 0 pyright errors |
| bandit clean | bandit clean |

See `reports/STARCORE-Platform-Audit-Report-2026-07-26.md` for the full
inventory, architecture review, and risk matrix.
