# ADR-020 — Legacy Root Layer Freeze

- **Status:** Accepted
- **Date:** 2026-08-06
- **Implements:** GADR-003 (STARCORE Architecture Governance Report)

## Context

Per ADR-018, the repository root (outside `platform/`) is non-authoritative
legacy scaffolding: 65 Termux/Android install scripts, ~411 generated JSON
files under `runtime/`, and stub Python modules under `autonomous/`,
`distributed/`, `ai_core/`, `ai_runtime/`, `knowledge/`, `knowledge_engine/`,
`mission_engine/`, `sdk/`, `agents/`, `api_gateway/`, `github_intelligence/`,
`hardening/`, root-level `security/`, `studio/`, `performance/`, `core/`,
`control_center/`, `automation/`, `tools/`, `bin/`, `cli/`, `templates/`,
`registry/`, and `sessions/`. Its final disposition (archive, partial
extraction, removal) has not yet been decided and depends on further input
(in particular, the Android/Termux question resolved separately in
ADR-024). Until that decision is made, the layer should not keep growing.

## Options

1. **No freeze** — leave the layer open to further additions until a
   disposition decision is made.
2. **Freeze now** — no new files, commits, or edits to the listed
   directories until each is explicitly re-classified by a follow-up
   decision; the layer is treated as a read-only historical artifact.
3. **Freeze and immediately archive** (`git mv` into an `archive/` prefix)
   in the same action.

## Decision

**Option 2.** The legacy root layer is frozen as of this ADR's date. No new
files are added to it, no existing files are edited within it, and no code
inside it is imported by `platform/` (per ADR-019). It remains in place,
unarchived, as a read-only historical record pending a separate archival or
removal decision.

## Consequences

- Any future session encountering these directories should treat them as
  frozen: read for historical context only, never extend.
- This ADR does not move or delete anything — archival (`git mv` into an
  `archive/` prefix) or removal is a distinct, separately-approved action,
  because it is a higher-risk, less-reversible-in-spirit operation than a
  freeze and deserves its own explicit confirmation.
- The freeze applies uniformly to all listed directories except where a
  later ADR carves out a specific exception (see ADR-024, which defines a
  forward path for the Android/Termux subtree specifically as a new,
  separate Edge Node concept rather than a continuation of the frozen
  code).

## Alternatives rejected

**Option 1** was rejected because it permits exactly the continued growth
this ADR exists to stop.

**Option 3** was rejected as premature at this checkpoint: archiving before
the Android/Termux disposition (ADR-024) is finalized in detail risks
moving content whose ultimate treatment is still being defined, and mixes
a low-risk decision (freeze) with a higher-risk one (bulk `git mv`) in a
single action. Archival remains the recommended next step after this ADR,
but as its own explicitly-approved change.
