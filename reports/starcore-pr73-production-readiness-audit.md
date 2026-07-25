# STARCORE Platform — PR #73 Production Readiness Audit

> Audit Date: 2026-07-25 | Mode: READ-ONLY / AUDIT ONLY | No code changes made

---

## 1. Executive Summary

PR #73 ("feat: session 2026-07-25 — observability, automation, cleanup, docs") is **OPEN, UNMERGED, and currently UNMERGEABLE** due to a `mergeable_state: "dirty"` on GitHub (main branch moved forward by one commit — PR #72 — after this branch was created). All nine action bundles are implemented and locally verified. All local quality gates pass. The GitHub Actions CI (`quality` + `docker-build`) has **not produced visible check runs** for this PR.

Seven findings were identified — zero P0, one P1 blocker (merge conflict), three P2/P3 code-quality issues, three P3 documentation/hygiene gaps. The codebase is in excellent overall health with 100% line coverage and zero CVEs; the findings below are pre-merge action items rather than fundamental flaws.

---

## 2. Audit Metadata

| Item | Value |
|---|---|
| Audit timestamp | 2026-07-25 |
| Auditor | Claude Code (claude-sonnet-4-6) |
| Mode | READ-ONLY — AUDIT ONLY — no changes made |
| Repository | Fatalerorr69/starcore-platform |
| Branch audited | claude/new-session-s52x55 |
| HEAD SHA | 4e278c2431e0c2c53ec356bc24848e948fb02dcf |
| PR | #73 |
| Python | 3.12.3 |
| uv | 0.8.17 |
| Source of truth | Live filesystem + git + GitHub API |

---

## 3. Repository State

| Property | Value | Status |
|---|---|---|
| Branch | claude/new-session-s52x55 | VERIFIED |
| HEAD SHA | 4e278c2 | VERIFIED |
| Working tree | clean (nothing to commit) | VERIFIED |
| Untracked files | none | VERIFIED |
| Modified files | none | VERIFIED |
| Staged files | none | VERIFIED |
| Commits ahead of main merge-base | 9 | VERIFIED |
| Merge base with origin/main | 3996433 | VERIFIED |
| origin/main current HEAD | 6f513fd | VERIFIED |
| Local merge-tree conflict markers | 0 | VERIFIED |

---

## 4. Git State

```
HEAD:     4e278c2  chore(reports): final session report — health 100/100, zero tech debt
          09dcf22  docs(TD-C05,TD-C06): document alembic check workflow and pin mkdocs below v2
          4d0cf37  chore(reports): finalize session report — C01,C03 EXECUTED, C02 corrected
          af4edc9  feat(C01): add Prometheus metrics endpoint and structured logging
          4f337f7  chore(C03): remove unused redis and nats-py dependencies
          873d1a3  chore(reports): update code report — B01,B02 EXECUTED, health score 97
          0b0b72d  feat(B01,B02): add scripts/ automation and starcore doctor/audit CLI commands
          371e071  reports: update code report for session claude/new-session-s52x55
          d14f5b0  chore: align Dockerfile to Python 3.12 and add pyright pre-commit hook
main:     6f513fd  Claude/new session s52x55 (#72)   ← 1 commit added to main after branch diverged
merge-base: 3996433
```

**Divergence root cause**: PR #72 was merged to `main` after this branch was created. The branch has not been rebased or merged-with `main` since then. GitHub reports `mergeable_state: "dirty"` as a result. Local `git merge-tree` shows **0 conflict markers**, so the conflict may be entirely in report/documentation files, but GitHub's computation has not resolved it.

---

## 5. PR #73 Verification

| Check | Result | Evidence |
|---|---|---|
| PR exists | YES | GitHub API: id=4131947270 |
| PR state | open | VERIFIED |
| Source branch | claude/new-session-s52x55 | VERIFIED |
| Target branch | main | VERIFIED |
| Merged | NO | merged=false |
| Mergeable | **NO** | mergeable_state="dirty" |
| Reviews (human) | 0 | get_reviews result |
| Reviews (bot) | Sourcery COMMENTED (failure) | VERIFIED |
| GitHub Actions CI | **NOT VISIBLE** | Only 3 external checks present |
| Socket Security (project) | SUCCESS | check run 89667392247 |
| Socket Security (PR alerts) | NEUTRAL | check run 89667512260 |
| Sourcery review | **FAILURE** | check run 89667393588 |
| Required checks passing | UNKNOWN (CI not visible) | NOT VERIFIED |
| Unresolved review comments | 3 (Sourcery) | VERIFIED — see §22 |
| Changed files | 19 | VERIFIED |
| Additions | 974 | VERIFIED |
| Deletions | 199 | VERIFIED |
| Commits | 9 | VERIFIED |

### CI Gap

The repository's `ci.yml` workflow triggers on `pull_request: branches: [main]`. Expected checks — `quality` (ruff, pyright, pip-audit, pytest) and `docker-build` — are absent from the check runs list. Possible explanations:
1. Workflow was not triggered because the PR was created via the GitHub MCP tool (not `gh` CLI or the web UI) and the dispatch may not have fired.
2. Workflow runs exist but were not returned in the first page of check runs.
3. GitHub Actions runner had no capacity at the time.

This must be confirmed before merging.

---

## 6. Action Bundle Verification

| ID | Claimed Status | Actual Status | Evidence | Commit | Risk |
|---|---|---|---|---|---|
| A01 | EXECUTED | **CONFIRMED** | `FROM python:3.12-slim` in Dockerfile | d14f5b0 | None |
| A02 | EXECUTED | **CONFIRMED** | pyright hook in `.pre-commit-config.yaml` | d14f5b0 | None |
| B01 | EXECUTED | **CONFIRMED** | `scripts/doctor.py`, `scripts/health.py` exist | 0b0b72d | See F-04 (subprocess) |
| B02 | EXECUTED | **CONFIRMED** | `starcore doctor` / `starcore audit` in CLI | 0b0b72d | See F-04, F-07 |
| B03 | EXECUTED | **CONFIRMED** | reports updated throughout session | 371e071–4e278c2 | None |
| C01 | EXECUTED | **CONFIRMED** | `packages/core/metrics.py`, `/metrics` endpoint, `STARCORE_LOG_JSON` | af4edc9 | See F-05, F-06 |
| C02 | NOT_NEEDED | **CONFIRMED** | `_snapshot_create/list/delete/rollback` in `packages/providers/proxmox/provider.py` lines 347–404, CLI `snapshot_app` in `apps/cli/main.py:31+`, `resource_actions.py` chain — fully implemented | N/A | None (runtime unverified) |
| C03 | EXECUTED | **CONFIRMED** | `redis` and `nats-py` absent from `pyproject.toml`; `redis_url`/`nats_url` absent from `config.py` | 4f337f7 | See F-08 (stale .env.example) |
| TD-C05 | EXECUTED | **CONFIRMED** | `docs/development.md` §Database migrations has throwaway-DB runbook; `CONTRIBUTING.md` has cross-reference | 09dcf22 | None |
| TD-C06 | EXECUTED | **CONFIRMED** | `pyproject.toml`: `mkdocs>=1.6.1,<2.0.0`, `mkdocs-material>=9.6.15,<10.0.0`; rationale in `docs/development.md` | 09dcf22 | None |

### C02 Implementation Chain (verified)

```
starcore snapshot create/list/delete/rollback
  ↓ apps/cli/main.py:550+ (snapshot_app typer commands)
  ↓ packages/core/resource_actions.py:execute_resource_action()
  ↓ packages/providers/proxmox/provider.py:execute()  (line 221-227)
  ↓ _snapshot_create (347), _snapshot_list (372), _snapshot_delete (384), _snapshot_rollback (404)
  ↓ proxmoxer API calls
Status: CODE IMPLEMENTED — RUNTIME NOT VERIFIED (Proxmox not accessible in sandbox)
```

---

## 7. Historical Report Discrepancies

| Claim | Historical Report | Current Evidence | Classification |
|---|---|---|---|
| "355 tests zelených" | 100/100 health | 354/355 on first run (flaky), 355/355 on second run | HISTORICAL DISCREPANCY — intermittent failure exists |
| "Nulový tech debt" | Zero remaining | 7 new findings identified (see §25) | HISTORICAL DISCREPANCY — tech debt exists |
| "redis/nats odstraněny" | Fully removed | Correct for pyproject.toml + config.py; BUT `.env.example` still has `STARCORE_REDIS_URL` and `STARCORE_NATS_URL` | HISTORICAL DISCREPANCY — partial removal |
| `postgres_url` field | Not mentioned | Still present in `config.py:25` — unused dead config | HISTORICAL OMISSION |

---

## 8. Test Audit

| Metric | Value | Status |
|---|---|---|
| Total tests collected | 355 | VERIFIED |
| Passed (run 1) | 354 | VERIFIED — 1 failure |
| Passed (run 2) | 355 | VERIFIED |
| Failed | 1 (intermittent) | VERIFIED — see F-03 |
| Skipped | 0 | VERIFIED |
| Warning | 1 (httpx/starlette deprecation) | VERIFIED |
| Property-based tests | 90 | VERIFIED (grep count) |
| Duration | ~36–53s | VERIFIED |

### Test Classification

| Category | Files | Notes |
|---|---|---|
| Unit | test_blueprints, test_orchestrator, test_providers, test_core | Mocked external I/O |
| Integration | test_api, test_migrations, test_schema_management | In-process SQLite |
| Property-based | test_property_based_*.py (6 files) | Hypothesis |
| CLI | test_cli | CliRunner, no real subprocess |
| AI | test_ai, test_property_based_ai | Mocked Anthropic client |
| Metrics | test_metrics | In-process HTTP, mocked event bus |
| Logger | test_logger | Loguru sink kwargs only |

### Coverage

| Metric | Value | Confidence |
|---|---|---|
| Line coverage | 100% | HIGH — verified by `--cov-report=term-missing` |
| Branch coverage | Not measured | UNKNOWN — not in CI config |
| Integration coverage | Partial | MEDIUM — external APIs fully mocked |
| Runtime coverage | NOT VERIFIED | LOW — no live stack tests |

### Untested scenarios (inferred, not verified)

- Anthropic API timeout / rate limit
- Proxmox connection failure during snapshot
- concurrent blueprint runs (race conditions)
- Docker socket unavailable at runtime
- SQLite WAL conflicts under concurrent writers
- Invalid API key with timing side-channel

---

## 9. Coverage Audit

- **Line coverage**: 100% of 1679 lines across packages and apps. **VERIFIED**.
- **Measurement**: `uv run pytest --cov --cov-report=term-missing` covers `packages/` and `apps/`.
- **Critical gap**: All external integrations (Anthropic API, Proxmox API, Docker socket) are mocked. 100% line coverage does NOT imply production-behavior coverage.

---

## 10. CI/CD Audit

| Gate | Status | Evidence |
|---|---|---|
| `uv lock --check` | PASS | Locally verified |
| `ruff check .` | PASS | "All checks passed!" |
| `ruff format --check .` | PASS | "74 files already formatted" |
| `pyright` | PASS | "0 errors, 0 warnings, 0 informations" |
| `pip-audit` | PASS | "No known vulnerabilities found" |
| `pytest -q --cov --cov-fail-under=80` | PASS | 354–355 passed (100% cov) |
| `alembic check` (CI pattern) | NOT RUN locally | Requires throwaway DB per docs/development.md |
| Docker build + /health smoke test | NOT RUN | Docker daemon not accessible in sandbox |
| GitHub Actions `quality` job | **NOT VISIBLE** | PR check runs don't include it |
| GitHub Actions `docker-build` job | **NOT VISIBLE** | PR check runs don't include it |

---

## 11. Dependency Audit

### Python dependencies (`pyproject.toml`)

- `redis` and `nats-py`: **ABSENT** — VERIFIED removed (C03)
- `mkdocs<2.0.0`, `mkdocs-material<10.0.0`: **PRESENT** — VERIFIED (TD-C06)
- `prometheus-client>=0.21.0`: PRESENT (C01)
- All others: unchanged from pre-session state
- `pip-audit`: **CLEAN** — 0 known CVEs

### Dead config field

`packages/core/config.py:25`: `postgres_url: str = "postgresql://starcore:starcore@localhost:5432/starcore"` — this field was NOT removed in C03 even though `redis_url` and `nats_url` were. It is unused by the application. Default value contains a weak credential (`starcore:starcore`) for a service not active by default.

### `.env.example` stale entries

`.env.example` still contains:
```
STARCORE_REDIS_URL=redis://localhost:6379
STARCORE_NATS_URL=nats://localhost:4222
```
These correspond to settings fields that were removed from `Settings`. They are now dead entries that will be silently ignored by `pydantic-settings` (due to `extra="ignore"`), but mislead contributors.

---

## 12. Docker Audit

| Check | Status | Evidence |
|---|---|---|
| Base image | `python:3.12-slim` | VERIFIED (A01) |
| Non-root user | YES — `starcore` user | VERIFIED |
| Healthcheck | YES | VERIFIED — `curl /health` every 30s |
| Multi-stage build | NO | Single stage (acceptable for current size) |
| Secrets in Dockerfile | NONE | VERIFIED |
| Docker Compose services | `api` (default) + `postgres`/`redis`/`nats` (scaffold profile) | VERIFIED |
| Postgres password in Compose | Env-var required (`${STARCORE_POSTGRES_PASSWORD:?...}`) | VERIFIED — old hardcoded `starcore` was fixed |
| `/var/run/docker.sock` mounted | YES | Required for Docker provider |
| `DOCKER_GID` group add | YES | Required for socket access without root |
| Docker daemon accessible | NO | Sandbox limitation — build not verifiable |

---

## 13. Runtime Audit

### Endpoints

| Endpoint | Auth | Status | Evidence |
|---|---|---|---|
| `GET /` | None | Implemented | In main.py |
| `GET /health` | None | Implemented — DB check only | VERIFIED in tests |
| `GET /diagnostics` | X-API-Key | Implemented | VERIFIED |
| `GET /metrics` | X-API-Key | Implemented | VERIFIED (C01) |
| `POST /blueprints/validate` | X-API-Key | Implemented | VERIFIED |
| `POST /blueprints/plan` | X-API-Key | Implemented | VERIFIED |
| `POST /blueprints/execute` | X-API-Key | Implemented | VERIFIED |
| `POST /ai/generate-blueprint` | X-API-Key | Implemented | VERIFIED |
| `POST /runs` | X-API-Key | Implemented | VERIFIED |
| `GET /runs/{run_id}` | X-API-Key | Implemented | VERIFIED |

### API security

- API key: `hmac.compare_digest` (constant-time) — **VERIFIED**
- API fails-closed (503) when no key configured — **VERIFIED**
- Rate limiting: `slowapi` per-IP, `/health` exempt — **VERIFIED**
- `/metrics` requires same API key as diagnostics — **VERIFIED**

### Runtime not verified

- Proxmox API connectivity — NOT ACCESSIBLE
- Docker provider via live socket — NOT ACCESSIBLE
- Anthropic API key validity — NOT ACCESSIBLE

---

## 14. Observability Audit

### Metrics (`packages/core/metrics.py`)

| Item | Status | Notes |
|---|---|---|
| Registry | Dedicated `CollectorRegistry` | Avoids test-suite duplicate-timeseries errors |
| `starcore_http_requests_total{method,path,status}` | Implemented | path uses route template (bounded cardinality) |
| `starcore_http_request_duration_seconds{method,path}` | Implemented | Histogram |
| `starcore_blueprint_tasks_total{provider,status}` | Implemented | Via EventBus subscription |
| `status` label type | **INT** (not str) | `response.status_code` is int; Prometheus convention is string — **see F-05** |
| Middleware docstring | **Inaccurate** | Says "GET /metrics" but runs on all routes — **see F-06** |
| Cardinality risk | LOW | Route template prevents per-ID explosion |
| Authentication | YES (X-API-Key) | VERIFIED |

### Structured Logging (`packages/core/logger.py`)

| Item | Status |
|---|---|
| Default mode | Human-readable text |
| JSON mode | `STARCORE_LOG_JSON=true` → `serialize=True` |
| Sink wired at startup | YES (import side-effect in main.py and cli/main.py) |
| Sensitive data exposure | No API keys logged — VERIFIED by grep |
| `diagnose=False` | YES — suppresses local-variable dumps in tracebacks |

---

## 15. Logging Audit

- Loguru `diagnose=False`: prevents accidental exposure of local variables (which could include API keys) in exception tracebacks — **VERIFIED**
- `enqueue=True`: async-safe logging — VERIFIED
- No `logger.info(f"key={key}")` patterns found in main source — VERIFIED
- JSON mode serializes full log record; no field filtering — field-level secrets could appear if inadvertently logged, but current code does not log request bodies or credentials

---

## 16. Security Audit

| Area | Finding | Severity | Evidence |
|---|---|---|---|
| Secrets in code | NONE FOUND | — | grep for key/password/token patterns |
| `.env` in repo | NO (gitignored) | — | `.gitignore`: `.env`, `.env.local` |
| `.env.example` | Present, no real secrets | — | VERIFIED |
| `postgres_url` default credential | `starcore:starcore` in `config.py` | P3-INFO | Field is dead (unused), but sets a weak default |
| subprocess in `apps/cli/main.py:79` | Dynamic `cmd` list | P3 | See F-04 — actually hardcoded; false positive |
| subprocess in `scripts/doctor.py:33` | Dynamic `cmd` list | P3 | See F-04 — actually hardcoded; false positive |
| Docker socket mount | `/var/run/docker.sock` | P3-INFO | Intentional (Docker provider) — not a vulnerability |
| API auth constant-time | `hmac.compare_digest` | — | SECURE |
| pip-audit | CLEAN | — | 0 CVEs |
| Socket Security (GitHub) | NEUTRAL/SUCCESS | — | External scan |

### Subprocess Audit (F-04 context)

Both subprocess usages flagged by Sourcery/opengrep are **developer tools** with hardcoded command lists:

`scripts/doctor.py:33` — `cmd` comes from the module-level constant `GATES: list[tuple[str, list[str]]]` — all entries are `["uv", "run", ...]` literals. No user input reaches `cmd`.

`apps/cli/main.py:79` — `cmd` is assembled from a hardcoded constant list in the `doctor()` function body. Same pattern.

**Assessment**: INFERRED false positive for command injection. No external input flows into `cmd` in either location. The finding is a static-analysis heuristic, not a real vulnerability. However, the flag is from a recognized SAST tool and should be addressed with a `# noqa` annotation or inline comment explaining why it is safe.

---

## 17. Proxmox / Infrastructure Audit

### Implementation (VERIFIED)

| Component | Status |
|---|---|
| `_snapshot_create` | Code-implemented: `proxmoxer` API call via asyncio thread |
| `_snapshot_list` | Code-implemented |
| `_snapshot_delete` | Code-implemented |
| `_snapshot_rollback` | Code-implemented (line 404) |
| `_require_snapshot_fields` | Validation helper — VERIFIED |
| Error handling | `try/except` in `execute_resource_action`; sets `TaskStatus.FAILED` |
| Authentication | Proxmox API token via `STARCORE_PROXMOX_*` env vars |
| Timeout | NOT IMPLEMENTED — no timeout on `asyncio.to_thread` calls |
| Retry | NOT IMPLEMENTED |

### Runtime

NOT VERIFIED — Proxmox not accessible in sandbox. Code is implemented and unit-tested with mocks.

---

## 18. AI Integration Audit

| Property | Anthropic | Notes |
|---|---|---|
| Implemented | YES | `packages/ai/generator.py` |
| Configured | Via `STARCORE_ANTHROPIC_API_KEY` env var | |
| Model | `STARCORE_ANTHROPIC_MODEL` (default: `claude-sonnet-5`) | |
| Client | `AsyncAnthropic` (async) | |
| Retry | NO | Exception caught and re-raised as `BlueprintGenerationError` |
| Timeout | NO | No `timeout=` parameter on `client.messages.create()` |
| Rate-limit handling | NO | HTTP 429 caught as generic Exception |
| Fallback | NO | |
| Observability | PARTIAL | Exception logged via `BlueprintGenerationError`; no metrics |
| Runtime verified | NO | API key not set in sandbox |

| Provider | Implemented | Tested | Runtime Verified | Production Ready |
|---|---|---|---|---|
| Anthropic | YES | YES (mocked) | NO | PARTIAL (no retry/timeout) |
| OpenAI-compatible | NO | NO | NO | NO |
| OpenRouter | NO | NO | NO | NO |
| Ollama | NO | NO | NO | NO |
| LiteLLM | NO | NO | NO | NO |
| vLLM | NO | NO | NO | NO |

---

## 19. MCP Audit

| Item | Status |
|---|---|
| MCP client | NOT IMPLEMENTED |
| MCP server | NOT IMPLEMENTED |
| MCP tools | NONE |
| MCP transport | N/A |

MCP is not part of the current platform scope. The session-level Claude Code tooling uses MCP (GitHub MCP server, etc.) but the STARCORE application itself has no MCP integration. This is by design for the current architecture.

---

## 20. AI-Native Workflow Audit

| Step | Automated | Tool |
|---|---|---|
| Code editing | YES | Claude Code |
| Quality gates | YES | `starcore doctor` / `scripts/doctor.py` |
| Runtime health | YES | `scripts/health.py` |
| Git audit | YES | `starcore audit` |
| PR creation | YES | GitHub MCP (this session) |
| CI monitoring | NO | Not implemented |
| PR review response | MANUAL | User approves |
| Deployment | NOT VERIFIED | Docker Compose |
| Infrastructure ops | NOT VERIFIED | Proxmox not accessible |

---

## 21. GitHub Audit

| Item | Status | Evidence |
|---|---|---|
| Open PRs | 1 (PR #73) | VERIFIED |
| Open issues | UNKNOWN | Not checked this session |
| Dependabot | Active | dependabot.yml present |
| Branch protection | UNKNOWN | `gh` CLI not available; main has PRs |
| CI workflows | ci.yml, docker-publish.yml, dependabot-auto-merge.yml | VERIFIED |
| Security alerts | UNKNOWN | Not accessible |
| Secret scanning | UNKNOWN | Not accessible |
| Tags | UNKNOWN | Not checked |

---

## 22. Documentation Audit

| Document | Status | Notes |
|---|---|---|
| README | PRESENT | Not audited in depth this session |
| `docs/development.md` | PRESENT, UPDATED | Alembic runbook + mkdocs cap rationale added (TD-C05/C06) |
| `CONTRIBUTING.md` | PRESENT, UPDATED | Alembic cross-reference added (TD-C05) |
| `docs/architecture.md` | PRESENT, UPDATED | Metrics + logging documented (C01) |
| ADRs | 5 present | Not audited in depth |
| Changelogs | 5 present | **No sprint-006 or sprint-007 changelog** — new features not documented per `CONTRIBUTING.md` policy |
| `docs/installation.md` | PRESENT | References removed Postgres/Redis/NATS services — may be stale |

### Sourcery review comments (open, unresolved)

1. **Metrics middleware docstring** says "GET /metrics" but middleware records all routes.
2. **Duplicate gate logic** between `scripts/doctor.py` and `starcore doctor` CLI command.
3. **`subprocess.run`** without static string (security flag) — in `apps/cli/main.py:79` and `scripts/doctor.py:33`.

---

## 23. Technical Debt

| ID | Description | State | Priority | Evidence | Recommendation |
|---|---|---|---|---|---|
| TD-NEW-01 | PR #73 merge conflict (dirty state) | OPEN | P1 | mergeable_state="dirty" | Rebase or merge main into branch |
| TD-NEW-02 | GitHub Actions CI not visible for PR #73 | OPEN | P1 | 0 quality/docker-build check runs | Verify CI triggered; re-push if needed |
| TD-NEW-03 | Flaky property-based test | OPEN | P2 | test_repository_list_known_provider_vmids_returns_saved_vmids fails ~50% in full suite | Investigate Hypothesis database/state leak; add explicit `@settings(suppress_health_check=...)` |
| TD-NEW-04 | `prometheus_client` status label is int not str | OPEN | P2 | `status=response.status_code` in main.py:125 | Change to `str(response.status_code)` |
| TD-NEW-05 | `postgres_url` dead config field remains | OPEN | P3 | config.py:25 — unused after C03 | Remove field and remove from `.env.example` |
| TD-NEW-06 | `.env.example` has stale REDIS_URL/NATS_URL entries | OPEN | P3 | .env.example lines 6-7 | Remove `STARCORE_REDIS_URL` and `STARCORE_NATS_URL` |
| TD-NEW-07 | Metrics middleware docstring inaccuracy | OPEN | P3 | packages/core/main.py:112 | Update docstring: "for all HTTP routes" |
| TD-NEW-08 | subprocess.run SAST flag (false positive, needs suppression) | OPEN | P3 | apps/cli/main.py:79, scripts/doctor.py:33 | Add inline comment or `# noqa` explaining why it is safe |
| TD-NEW-09 | Duplicate gate definitions (scripts/doctor.py vs starcore doctor) | OPEN | P4 | B01 vs B02 | Extract shared `GATES` constant to shared module |
| TD-NEW-10 | No sprint-006/007 changelog entries | OPEN | P4 | docs/changelog/ — 5 files max sprint-005 | Add sprint-006.md covering C01, B01/B02 |
| TD-NEW-11 | AI generator: no retry/timeout | OPEN | P4 | packages/ai/generator.py — no timeout param | Add `timeout=` to Anthropic client call |
| TD-NEW-12 | Proxmox snapshot: no timeout on asyncio.to_thread | OPEN | P4 | provider.py — `asyncio.to_thread` calls | Wrap with `asyncio.wait_for` |

---

## 24. Production Readiness Matrix

| Domain | Status | Confidence | Evidence |
|---|---|---|---|
| Code Quality | PASS | HIGH | Ruff format+lint, pyright 0 errors |
| Tests | PASS (flaky) | MEDIUM | 354–355/355; 1 intermittent failure |
| Coverage | 100% line | HIGH | `--cov-report=term-missing` |
| CI/CD | PARTIAL | MEDIUM | Local gates pass; GitHub Actions CI not confirmed for PR |
| Security | PASS | HIGH | 0 CVEs, no secrets in code, constant-time key comparison |
| Dependencies | PASS | HIGH | pip-audit clean; version caps in place |
| Docker | CONFIGURED | MEDIUM | Build not verifiable (no daemon); config is correct |
| Runtime | NOT VERIFIED | LOW | No live stack accessible in sandbox |
| Database | IMPLEMENTED | MEDIUM | SQLite + Alembic; single migration; fast-fail on drift |
| Proxmox | IMPLEMENTED | LOW | Code verified; runtime NOT accessible |
| Infrastructure | NOT VERIFIED | LOW | Sandbox environment |
| AI (Anthropic) | PARTIAL | MEDIUM | Implemented + tested (mocked); no retry/timeout |
| MCP | NOT IMPLEMENTED | N/A | Out of scope |
| Observability | IMPLEMENTED | MEDIUM | /metrics authenticated, middleware records all routes |
| Logging | IMPLEMENTED | HIGH | loguru configured, JSON mode available |
| Automation | IMPLEMENTED | HIGH | scripts/doctor.py, starcore doctor/audit |
| GitHub | OPEN PR | HIGH | PR exists, CI gap needs resolution |
| Documentation | GOOD | HIGH | Alembic runbook added, mkdocs capped, ADRs present |

---

## 25. Findings

### F-01 — P1 BLOCKER — PR #73 Has Merge Conflict

**Description**: GitHub reports `mergeable_state: "dirty"`. `origin/main` is at `6f513fd` (PR #72 merged after this branch diverged from `3996433`). The branch has not been rebased.

**Impact**: PR cannot be merged.

**Evidence**: GitHub API `mergeable: null`, `mergeable_state: "dirty"`.

**Action**: Rebase `claude/new-session-s52x55` onto `origin/main` (or merge main into branch), resolve any conflicts, push.

---

### F-02 — P1 — GitHub Actions CI Not Confirmed for PR #73

**Description**: PR check runs show only third-party tools (Sourcery, Socket). The `quality` and `docker-build` GitHub Actions jobs from `ci.yml` are not present.

**Impact**: Merge gates for required CI are unknown.

**Evidence**: `get_check_runs` returned 3 entries; none are from `ci.yml`.

**Action**: Confirm CI triggered (check Actions tab); re-push to trigger if needed.

---

### F-03 — P2 — Flaky Property-Based Test

**Description**: `tests/test_property_based_core.py::test_repository_list_known_provider_vmids_returns_saved_vmids` failed on first full-suite run (354/355 passed), passed in isolation and on second full-suite run.

**Impact**: Intermittent CI failures; undermines confidence in the test suite.

**Evidence**: `1 failed, 354 passed, 1 warning in 35.97s` (run 1); `355 passed` (run 2 and isolation).

**Action**: Investigate state leak — likely a Hypothesis database interaction with a shared in-process component. Consider `@settings(suppress_health_check=[HealthCheck.too_slow])` or explicit state reset.

---

### F-04 — P3 — subprocess.run SAST Flag (False Positive, Needs Suppression)

**Description**: Sourcery/opengrep flagged `subprocess.run(cmd, ...)` in `apps/cli/main.py:79` and `scripts/doctor.py:33` as potential command injection. Audit confirms `cmd` is a hardcoded list in both locations; no user input reaches it.

**Impact**: False positive fails Sourcery review check; may cause noise in future SAST runs.

**Evidence**: Sourcery review comment; code inspection confirms hardcoded constants.

**Action**: Add `# subprocess invocation is safe: cmd is a hardcoded constant list` inline comment. Consider `# noqa: S603` if using Bandit.

---

### F-05 — P3 — Prometheus Status Label Is int, Not str

**Description**: `HTTP_REQUESTS_TOTAL.labels(..., status=response.status_code).inc()` passes `status_code` as an integer. Prometheus label values are strings; prometheus_client converts silently, but this creates inconsistency and is non-conventional.

**Evidence**: `packages/core/main.py:125`.

**Action**: Change to `status=str(response.status_code)`.

---

### F-06 — P3 — Metrics Middleware Docstring Inaccurate

**Description**: Docstring says "Record HTTP request count and latency for GET /metrics." The middleware actually records metrics for **all HTTP routes**.

**Evidence**: `packages/core/main.py:112-120`; Sourcery review comment.

**Action**: Update docstring to "Record HTTP request count and latency for all HTTP routes."

---

### F-07 — P3 — Stale `.env.example` Entries and Dead `postgres_url` Config Field

**Description**: After C03 removed `redis_url` and `nats_url` from `Settings`, `.env.example` still contains `STARCORE_REDIS_URL` and `STARCORE_NATS_URL`. Additionally, `postgres_url` remains in `Settings` (not removed in C03) with a default weak credential `starcore:starcore`.

**Evidence**: `.env.example:6-7`; `packages/core/config.py:25`.

**Risk**: Misleads contributors; `postgres_url` default credential appears in any log or debug dump of `Settings`.

**Action**: Remove `STARCORE_REDIS_URL`, `STARCORE_NATS_URL` from `.env.example`; remove `postgres_url` from `Settings` and from `.env.example`.

---

## 26. Immediate Recommendations (Pre-Merge)

| Priority | Action | File | Why |
|---|---|---|---|
| P1 | Rebase branch onto main (resolve merge conflict) | Branch | PR is unmergeable |
| P1 | Confirm GitHub Actions CI triggered; re-push if not | ci.yml | Required checks must pass |
| P2 | Investigate and fix flaky property-based test | tests/test_property_based_core.py | Intermittent CI failures |
| P3 | Change `status=str(response.status_code)` | packages/core/main.py:125 | Prometheus label type |
| P3 | Update metrics middleware docstring | packages/core/main.py:112 | Accuracy; Sourcery flag |
| P3 | Add SAST suppression comment for subprocess calls | apps/cli/main.py:79, scripts/doctor.py:33 | Sourcery failure |

---

## 27. Near-Term Recommendations

| Priority | Action | File |
|---|---|---|
| P3 | Remove `postgres_url` from Settings | packages/core/config.py |
| P3 | Remove stale REDIS_URL/NATS_URL from .env.example | .env.example |
| P4 | Extract shared GATES constant (doctor.py + CLI dedup) | New: packages/core/doctor_gates.py |
| P4 | Add sprint-006.md changelog (C01, B01/B02) | docs/changelog/ |
| P4 | Add `timeout=30` to Anthropic client.messages.create() | packages/ai/generator.py |
| P4 | Add `asyncio.wait_for` to Proxmox snapshot calls | packages/providers/proxmox/provider.py |

---

## 28. Strategic Recommendations

| Area | Recommendation | Benefit | Complexity |
|---|---|---|---|
| Testing | Add `asyncio.wait_for` timeouts + retry scenarios to provider tests | Catches network hangs in CI | Medium |
| Testing | Measure branch coverage (add `--cov-branch`) | Reveals conditional logic gaps | Low |
| AI | Add retry with exponential backoff to Anthropic client | Resilience to transient failures | Low |
| Observability | Add `starcore_blueprint_runs_total{status}` counter for full-run tracking | Better operational visibility | Low |
| Security | Document why `postgres_url` default exists (or remove it) | Reduces credential confusion | Low |
| CI | Add `alembic check` result verification to PR template checklist | Prevents migration drift | Low |
| Docker | Consider multi-stage build to reduce image size | Smaller attack surface | Medium |
| MCP | Evaluate MCP server for STARCORE (expose blueprint ops as tools) | AI-native infra management | High |

---

## 29. Automation Opportunities

| Opportunity | Benefit | Complexity | Prerequisites |
|---|---|---|---|
| `starcore release-check` CLI command | Verifies PR is ready: CI green, no conflicts, changelog entry | Low | None |
| `starcore verify` (post-merge smoke test) | Calls /health, /diagnostics, /metrics against live instance | Low | Live instance |
| GitHub Action: auto-rebase PR on main push | Keeps PRs always mergeable | Medium | Repo admin perms |
| GitHub Action: Dependabot auto-merge for patch/minor | Reduces manual dep work | Low | PR checks passing |
| AI PR reviewer (Claude Code) | Flags F-03 to F-07 class issues automatically | High | Claude Code subscription |
| `starcore audit --security` | SAST scan summary in CLI | Medium | bandit/semgrep |
| Hypothesis database persistence in CI | Finds regressions across runs | Low | pytest-hypothesis CI config |

---

## 30. Verified vs Claimed vs Unknown

| Category | Items |
|---|---|
| **VERIFIED** | All 10 action bundles (A01–TD-C06); all local quality gates; 355 tests collected; 100% line coverage; Dockerfile Python 3.12; non-root container; redis/nats removed from pyproject.toml + config.py; metrics endpoint authenticated; loguru sink wired; mkdocs version caps; alembic runbook in docs; snapshot chain code-implemented; .env gitignored; constant-time API key comparison |
| **INFERRED** | subprocess false positive (no user input flows to cmd — code inspected but dynamic analysis not performed); flaky test root cause (Hypothesis state leak assumed, not confirmed) |
| **CLAIMED** | "100% coverage" (VERIFIED locally); "0 open PRs" (INACCURATE — PR #73 is open); "nulový tech debt" (INACCURATE — 12 new findings) |
| **NOT VERIFIED** | GitHub Actions CI results for PR #73; Proxmox API connectivity; Docker container build; Anthropic API key validity; branch protection rules; Docker socket access at runtime |
| **UNKNOWN** | Open GitHub issues count; security alert state; secret scanning results; image build time |

---

## 31. Final Assessment

**Status: READY FOR MERGE — PENDING PRE-MERGE BLOCKERS**

The codebase is in excellent shape. All nine action bundles are correctly implemented, all local quality gates pass, line coverage is 100%, and zero CVEs are present. The PR is blocked from merging by a merge conflict (main moved forward) and unconfirmed GitHub Actions CI results — both are straightforward to resolve. Six additional non-blocking findings (F-03 through F-07) should ideally be addressed in this PR or immediately after.

| Dimension | Rating |
|---|---|
| Code quality | EXCELLENT |
| Test coverage | HIGH (100% line; flaky test caveat) |
| Security | GOOD (one SAST flag is false positive; postgres_url default is informational) |
| Mergeability | BLOCKED (merge conflict) |
| CI | UNCONFIRMED |
| Documentation | GOOD |
| Production readiness | MEDIUM (runtime not verified; no retry/timeout on external calls) |

---

## 32. Recommended Next Step

**Resolve the merge conflict** by rebasing `claude/new-session-s52x55` onto `origin/main` and pushing, then confirm GitHub Actions CI passes. While doing so, fix F-05 (`str(response.status_code)`), F-06 (middleware docstring), and F-04 (subprocess comment) to clear the Sourcery review — all three are one-line changes.
