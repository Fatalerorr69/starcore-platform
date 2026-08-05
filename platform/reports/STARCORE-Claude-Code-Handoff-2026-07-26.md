# STARCORE Platform — Claude Code Handoff

**Purpose:** Enough context for a fresh Claude Code session to continue
autonomously, without re-deriving what this session already established.
**Do not trust this document over the repository.** Verify the commit SHA
and re-run the baseline gates below before acting on anything else here.

---

## 1. Repository

- URL: `https://github.com/Fatalerorr69/starcore-platform`
- Branch this cycle's work is on: `claude/p0-p1-runbook-implementation`
  (not yet merged as of this writing — see §9)
- Base it was built from: `main` @ `e4c3b8f`
- Commit at handoff time: `d54e0ec`

## 2. What this cycle covered

Full P0 + P1 from `STARCORE Claude Code Autonomous Completion &
Optimization Runbook (2026-07-26)`. **P2 was explicitly deferred by user
direction, not left incomplete by accident.** See
`reports/STARCORE-Claude-Code-Implementation-Report-2026-07-26.md` for the
complete record (findings reconciliation table, every change, every
validation run).

## 3. Current architecture (delta from what CLAUDE.md described before this cycle)

- `depends_on` is now a **success gate** on both execution paths
  (`Scheduler`, `BlueprintExecutor`), not just an ordering constraint —
  `TaskStatus.SKIPPED_DEPENDENCY_FAILED`. See ADR-010.
- `packages/core/security.py` is the one place secret redaction lives —
  extend it, don't reimplement masking locally, if a future endpoint or
  provider needs it.
- Plugins are explicitly documented as **not sandboxed**
  (`docs/plugins.md`, ADR-011) — this was already true, just undocumented
  before.
- `docs/` gained `cli.md`, `api.md`, `security.md`, `plugins.md`,
  `test-matrix.md` — all generated from the actual code, not
  hand-maintained prose; if you add a route/command, update the matching
  page in the same PR or it will drift.
- `Dockerfile` is multi-stage now; `docker-compose.yml`'s `api.build` is
  still just `build: .` (no compose-level changes needed for this).

Everything else in `CLAUDE.md` (architecture layering, module roles not
listed above, execution paths, schema management, test isolation) is
unchanged and still accurate — it was re-verified, not assumed, during
this cycle (§3 of the Implementation Report).

## 4. Completed work (this cycle)

See the Implementation Report's §4 for the exact commit list. In short:
ADR-010/011/012, `core/security.py` + redaction tests, plugin docs,
`--non-interactive` removal, CLI/API/security/test-matrix reference docs,
Alembic rollback-procedure docs, multi-stage Docker build + `--no-dev` +
`--no-sync`, `mkdocs build --strict` CI gate, CLAUDE.md/README sync.

## 5. Pending work (P2 — deferred, ready to resume)

In the runbook's own suggested order (§16–20 there), each independent —
no ordering dependency between them:

1. **Request-correlation ID** (`STARCORE-Next-Steps-Proposal.md` from the
   prior audit already scoped this: FastAPI middleware,
   `contextvars.ContextVar`, `X-Request-ID` accept-or-generate, wire into
   `core/logger.py`'s Loguru sink). Estimate: half a day including tests.
2. **`snapshot rollback` dry-run diff** — show current vs. target
   snapshot state before the destructive rollback, matching the existing
   `blueprint plan` → `blueprint run` pattern. `apps/cli/main.py`'s
   `snapshot_rollback()`/`_run_snapshot_action()` are the entry points;
   check what state the Proxmox API actually exposes before promising a
   diff (only show verified differences, per the runbook's own guidance
   — don't fabricate a diff the API can't back up).
3. **Provider concurrency policy** — audit whether a per-provider
   concurrency limit (bounded semaphore) is needed now that
   `_connect_lock` only serializes `connect()`, not `execute()`. Current
   read (from this cycle's work, not independently re-audited): with only
   two providers and typical homelab scale, this is not yet a demonstrated
   need — write the ADR documenting that decision explicitly rather than
   adding a semaphore speculatively, unless a real requirement has
   surfaced by the time you pick this up.
4. **README "What's Planned, Not Built Yet" section** — every row in it
   currently says `Done`; either rename the section or fold it into "What
   Works Today" if genuinely nothing is left unimplemented. Purely
   cosmetic, ~15 minutes.
5. **`docker compose config`'s eager interpolation wrinkle** (Implementation
   Report §16) — cosmetic, does not affect real usage, lowest priority of
   everything on this list.

## 6. Known risks (carried forward, not new)

- Nothing new from this cycle beyond what's in §16 of the Implementation
  Report (the `docker compose config` wrinkle). No P0/P1 item was left
  open.

## 7. Test status

470 passed, 100.00% coverage, 0 ruff/pyright errors, bandit clean,
pip-audit clean, `uv lock --check` clean, `mkdocs build --strict` clean,
Alembic upgrade+check clean against a throwaway DB — all reproducible with
the commands in §9 below.

## 8. Quality gate status

All green — see Implementation Report §9 for the full table including the
one pre-existing, unrelated environment limitation (`pre-commit`'s
isolated pyright hook) and the one pre-existing, unrelated
`docker compose config` wrinkle.

## 9. Exact commands to reproduce validation

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pip-audit
uv run bandit -r packages/ apps/ scripts/ -ll -q
uv run pytest -q --cov --cov-report=term-missing --cov-fail-under=100
uv lock --check
STARCORE_DATABASE_URL=sqlite:///./ci-check.db uv run alembic upgrade head
STARCORE_DATABASE_URL=sqlite:///./ci-check.db uv run alembic check
rm ci-check.db
uv run mkdocs build --strict

# Docker (needs a running daemon; in a sandboxed environment with an
# intercepting egress proxy, see /root/.ccr/README.md's "docker build /
# docker run" section for the exact workaround used this cycle — never
# ship the workaround, it's local-verification-only):
docker build -t starcore-platform:local .
docker run -d --name starcore-check -p 8000:8000 \
  -e STARCORE_DATABASE_URL=sqlite:////data/starcore.db \
  starcore-platform:local
curl -sf http://localhost:8000/health
docker rm -f starcore-check
```

## 10. Database / migration status

Alembic-authoritative, one revision (`0001_initial_schema`), no drift.
Unchanged this cycle except documentation (rollback procedure added to
`docs/development.md`).

## 11. Docker status

Multi-stage, non-root, healthchecked, `--no-dev`, no runtime PyPI
dependency (`uv run --no-sync`). Verified end-to-end this cycle against a
live daemon — see Implementation Report §14.

## 12. Documentation status

`mkdocs build --strict` passes. Nav is complete for every page under
`docs/`. `docs/test-matrix.md` should be kept current whenever tests are
added/removed for an area it tracks.

## 13. Rollback instructions

See Implementation Report §17. Every commit in this cycle is small,
independently revertible, and touches a coherent, single concern.

## 14. This branch's PR status

As of this handoff, `claude/p0-p1-runbook-implementation` has **not** been
opened as a PR yet — that is the next immediate action for whoever
(human or Claude Code) picks this up, unless the current session is about
to do it itself. Check `git log origin/main..HEAD` and
`gh pr list`/the GitHub UI before assuming.
