# Sprint 017 — Release Workflow Gate Parity & mkdocs Nav Sync

**Date:** 2026-07-26
**Branch:** `claude/new-session-h38k71`
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### A — `release.yml` quality gate parity with `ci.yml`
The release workflow (triggered by pushing a `v*.*.*` tag, creates the
GitHub Release) only ran `ruff check`, `pyright`, and
`pytest --cov-fail-under=80` — a materially weaker gate than `ci.yml`'s,
and an 80% coverage floor when the rest of the repository enforces 100%
(same drift pattern previously caught as COV-001 in sprint-011).

Brought to full parity: added `uv lock --check`, `pip-audit`, Bandit SAST,
gitleaks secret scanning, `alembic check`, and `mkdocs build --strict`;
raised the coverage floor to 100%. A tag now gets the same defense-in-depth
as a PR merge, rather than relying solely on the assumption that the tagged
commit already passed `ci.yml` on `main`.

### B — mkdocs nav: 3 orphaned pages
`mkdocs build --strict` passed but reported three doc pages that existed on
disk but weren't reachable from the generated site's navigation:
`docs/architecture/current-state.md`, `docs/testing/test-strategy.md`, and
`docs/operations/repository-stabilization.md` (all added during the prior
session's repository-stabilization work, PR #90). Added to `mkdocs.yml` nav
as "Current State", "Test Strategy", and "Operations Runbook" respectively.

### C — README Repository Structure: missing directories
The tree diagram omitted `packages/ai/` (pluggable AI blueprint generation)
and `scripts/` (standalone doctor/health scripts) despite both being
established, documented parts of the codebase. Added both.

## Test counts
| Before | After |
|--------|-------|
| 470 passed | 470 passed |
| 100% coverage | 100% coverage |
| 0 pyright errors | 0 pyright errors |
| bandit clean | bandit clean |
