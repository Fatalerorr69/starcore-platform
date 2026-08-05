# Sprint 014 — Environment Detection Expansion & Doctor Consistency

**Date:** 2026-07-25
**Branch:** `claude/new-session-w47t28` (continuation after PR #82 merge)
**Mode:** MODE 5 — CONTROLLED AUTONOMY

## Changes

### `starcore doctor`: runtime_environment for consistency
Follow-up to sprint-013's ENV-001: `starcore doctor` now reports the same
`runtime_environment` detection as `audit` and `diagnose`, in both `--json`
output and the Rich table title, so all three CLI commands expose deployment
context consistently.

### Environment detection expansion
`packages/core/environment.py` grew from one check to four, each independent
and composable:

- `detect_runtime_environment()` — unchanged: `proxmox-host` / `container` /
  `local`, fast, local-only.
- **New** `detect_os_platform()` — OS family, release, and WSL (Windows
  Subsystem for Linux) detection via `/proc/version`. Fast, local-only;
  wired into `starcore audit`'s output (`os_platform` field / "OS platform"
  table row). Answers the "local PC" nuance the 3-way split couldn't:
  a Windows dev machine running STARCORE under WSL behaves differently
  (filesystem, networking) than native Linux.
- **New** `detect_cloud_provider()` — bounded-timeout (250ms per provider)
  probe of the AWS/GCP/Azure link-local metadata endpoints. Distinguishes
  "container on a cloud VPS" from "container on your local machine", which
  `runtime_environment` alone cannot. Deliberately *not* called from
  `audit`/`doctor` (documented as instant, local-only commands) — only from
  `run_diagnostics()` (`GET /diagnostics`, `starcore diagnose`), which
  already makes comparable network calls to Docker/Proxmox and is the
  documented "deep" check. Never raises; a network error or timeout is
  treated the same as "not this provider" and the whole probe adds ~0.3s
  in the common case (all three unreachable, e.g. this dev sandbox).
- **New** `classify_client_platform()` — pure User-Agent classification
  (`browser-desktop` / `browser-mobile` / `cli-or-script` / `unknown`).
  Wired into `GET /diagnostics`'s new `client` field, reporting which kind
  of client is *currently calling* the API (e.g. confirming a request came
  from a mobile/Android browser vs. a script) — a per-request concern,
  distinct from server-side environment detection.

`run_diagnostics()`'s response gained `environment_details` (`os_platform` +
`cloud_provider`); `GET /diagnostics` gained `client` (`user_agent` +
`platform`). `starcore diagnose`'s Rich-table output gained a
"Runtime environment: <env> (<cloud_provider>)" line when a cloud provider
is detected.

24 new tests (7 → 31 in `test_environment.py`, plus new API and CLI tests)
cover all branches: WSL/non-WSL, unreadable `/proc/version`, each cloud
provider match (including AWS's IMDSv2 401 case), all-unreachable, all four
client-platform buckets, and the CLI/API wiring.

## Test counts
| Before | After |
|--------|-------|
| 414 passed | 442 passed |
| 100% coverage | 100% coverage |
| 0 pyright errors | 0 pyright errors |
| bandit clean | bandit clean |
