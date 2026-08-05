# Sprint 010 — CLI Output Flags, Bandit SAST Gate & Nightly Security Audit

**Date:** 2026-07-25
**Branch:** `claude/starcore-discovery-audit-idto7s` → merged as PR #78
**Tracking IDs:** CI-001, CI-002, AUTO-001
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### CI-001 — `--json` / `--quiet` / `--non-interactive` output flags
Added machine-readable output flags to three CLI commands:

**`starcore doctor`**
- `--json`: emits `{"gates": [...], "passed": N, "failed": N}` to stdout
- `--quiet`: suppresses all output; rely on exit code only
- `--non-interactive`: disables interactive prompts (safe for CI/cron/systemd)
- `--fast`: skips test execution; checks lint, types, and security only

**`starcore audit`**
- `--json`: emits `{"checks": [...], "passed": N, "failed": N}` to stdout
- `--quiet` / `--non-interactive`: same semantics as `doctor`

**`starcore diagnose`**
- `--json`: emits structured diagnostic JSON to stdout
- `--quiet`: suppresses table output

These flags make all CLI quality gates consumable by CI pipelines, monitoring
scripts, and external orchestrators without screen-scraping.

### CI-002 — Bandit SAST integrated as a CI quality gate
`uv run bandit -r packages/ apps/ scripts/ -ll -q` added to the `quality` job
in `.github/workflows/ci.yml` between `pip-audit` and `pytest`. Any
medium-or-higher-severity finding now blocks the PR merge.

Two `# nosec` suppressions committed with documented rationale:
- `B104` (`packages/core/config.py`): binding `0.0.0.0` is intentional in
  a container — the comment explains the deployment context.
- `S603` (`apps/cli/main.py`, `scripts/doctor.py`): `subprocess.run()` is
  called with hardcoded constant command lists, not user-controlled strings.

Bandit is also added to `[dependency-groups]` in `pyproject.toml` alongside
`pre-commit` so it is available for local `uv run bandit` invocations.

### AUTO-001 — Nightly scheduled security audit
New `.github/workflows/security-nightly.yml` runs daily at **02:00 UTC** and on
`workflow_dispatch` (manual trigger). The workflow:

1. Installs Python 3.12 and all dev dependencies via `uv`
2. Verifies `uv lock --check` (lockfile consistency)
3. Runs `uv run pip-audit` (dependency CVE scan)
4. Runs `uv run bandit -r packages/ apps/ scripts/ -ll -q` (SAST)

This provides continuous vulnerability coverage independent of the PR cycle.

## Test counts
| Before | After |
|--------|-------|
| 366 passed | 384 passed |
| 0 warnings | 0 warnings |
| 100% coverage | 100% coverage |

18 new tests added to `tests/test_cli.py` covering all `--json`, `--quiet`,
`--non-interactive`, and `--fast` flag combinations for `doctor`, `audit`, and
`diagnose`.
