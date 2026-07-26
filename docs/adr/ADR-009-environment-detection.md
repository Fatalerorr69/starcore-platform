# ADR-009 — Environment Detection: Runtime, OS, Cloud Provider, Client

**Date:** 2026-07-25
**Status:** Accepted
**Deciders:** Core team

---

## Context

STARCORE can run in genuinely different contexts — directly on a Proxmox VE
node, in a Docker container (locally or on a cloud VPS), or as a bare process
on a developer's workstation (including under WSL on Windows) — and operators
had no way to confirm which one a given instance was actually running in
short of inspecting it by hand. Support/debugging conversations routinely
needed to establish this before anything else ("is this on the Proxmox box
itself, or a container somewhere?").

A single sprint (013) added a first, 3-way `runtime_environment` check
(`proxmox-host` / `container` / `local`). A follow-up (sprint 014) found that
split still couldn't answer two questions operators actually asked: whether
"local" meant native Linux or a Windows/WSL dev box, and whether "container"
meant a machine on the local network or a cloud VPS.

## Decision

Four independent, composable checks live in `packages/core/environment.py`,
each with a distinct cost profile that determines where it's wired in:

| Check | Cost | Wired into |
|---|---|---|
| `detect_runtime_environment()` | fast, local filesystem reads | `audit`, `doctor`, `diagnose`, `/diagnostics` |
| `detect_os_platform()` | fast, local filesystem reads | `audit`, `diagnose`, `/diagnostics` |
| `detect_cloud_provider()` | async, bounded-timeout network probe (~250ms × up to 3) | `diagnose`, `/diagnostics` only |
| `classify_client_platform()` | pure string classification, no I/O | `/diagnostics` only (per-request) |

The line is drawn at network I/O: `audit` and `doctor` are documented as
instant, local-only commands, so `detect_cloud_provider()` is deliberately
excluded from both — adding an unexpected network dependency to a command
promising instant local output would be a behavior regression, not an
enhancement. `run_diagnostics()` (`diagnose` / `GET /diagnostics`) already
makes comparable network calls to the Docker daemon and Proxmox API, so it's
the natural home for one more bounded probe.

`detect_cloud_provider()` probes the well-known AWS/GCP/Azure link-local
metadata endpoints (169.254.169.254, metadata.google.internal) with a short
per-provider timeout and never raises: a network error, timeout, or
unexpected response is treated identically to "not this provider". On a
homelab machine or Proxmox node these addresses are normally unreachable, so
every probe fails fast (measured ~0.3s total for all three in a sandboxed
dev environment) rather than hanging.

`classify_client_platform()` is a pure function over a `User-Agent` string —
no probing, no lookahead — because it answers a different kind of question
("what is calling right now") than the other three ("what am I running on").
It's wired only into `GET /diagnostics`, which is the one place a per-request
concern like "who is asking" makes sense; `audit`/`doctor`/`diagnose` are
invoked directly by an operator, with no meaningful "client" distinct from
the operator themselves.

## Consequences

**Positive**
- Operators get an immediate, explicit answer to "where am I running" and
  "who's calling" without needing shell access or log archaeology.
- The instant/local vs. deep/networked split is enforced structurally (which
  function is imported where), not just documented — `audit`/`doctor` cannot
  accidentally gain network latency by a future edit importing the wrong
  detector.

**Negative / Trade-offs**
- `detect_cloud_provider()` is a heuristic, not a source of truth: a cloud
  VM with its metadata endpoint firewalled off from the guest OS (some
  hardened images do this) will report `cloud_provider: null` even though
  it is, in fact, on that cloud.
- `classify_client_platform()`'s User-Agent parsing is trivially spoofable
  and explicitly documented as such — it's operator-facing diagnostic
  information, not a security or access-control signal.
- Four separate functions (vs. one that returns everything) means callers
  must import exactly what they need, which is more typing than a single
  "get everything" call — accepted deliberately so the cost/wiring boundary
  above stays visible at every call site.

## Alternatives considered

- **A single `get_environment_info()` returning all four dimensions
  unconditionally**: rejected — would force `audit`/`doctor` to either pay
  for the network probe every time or silently receive stale/null data,
  hiding the fast/local vs. slow/networked distinction inside the function
  instead of at the call site.
- **IMDSv2-only AWS detection (token-based)**: rejected in favor of also
  accepting IMDSv1's simpler unauthenticated response and the 401 that a
  hardened IMDSv2-only instance returns to an unauthenticated probe — both
  cases still confirm "this is AWS" without needing a token exchange, which
  would add a second round trip for information this check doesn't need
  (which cloud, not instance identity).
