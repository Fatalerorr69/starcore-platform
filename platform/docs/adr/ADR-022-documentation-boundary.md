# ADR-022 — Documentation Boundary

- **Status:** Accepted
- **Date:** 2026-08-06
- **Implements:** GADR-006 (STARCORE Architecture Governance Report)

## Context

`platform/docs/` (plus `platform/README.md`, `platform/CHANGELOG.md`, and
`platform/docs/adr/`) is accurate, actively maintained, and cross-checked
against the code by the Regression Sentinel's ADR-count probe. The
repository root, by contrast, has no README and no documentation describing
the legacy scaffolding's actual (non-)function. Repeated bootstrap-style
prompts in this project's history each proposed introducing a new,
standalone documentation framework at the repository root — which would
create a second, competing documentation surface rather than extending the
one that already works.

## Options

1. **No boundary** — allow documentation to be created wherever a session
   judges convenient, including at the repository root.
2. **Single documentation boundary** — all new documentation is added to
   `platform/docs/` (or `platform/.starcore/memory/` for internal
   session/knowledge state); no new documentation trees are created at the
   repository root.
3. **Mirror documentation** — maintain a root-level summary in addition to
   `platform/docs/`.

## Decision

**Option 2.** New documentation is added exclusively to `platform/docs/`
(user-facing: README, architecture, ADRs, operations, security) or
`platform/.starcore/memory/` (internal cross-session knowledge: risks,
decisions, pending work). No new documentation directories or frameworks
are created at the repository root. If the legacy root layer (ADR-020) is
later archived, at most one short pointer document is added explaining
what was archived and why — not a parallel documentation tree.

## Consequences

- Future architecture, process, or governance documentation (including any
  future SAEF-style proposal) is captured as ADRs or memory files inside
  `platform/`, per this ADR and ADR-023.
- `platform/docs/ROADMAP.md` (introduced alongside this ADR set) fills the
  one confirmed documentation gap identified by the discovery audit,
  consistent with this boundary.
- This ADR does not require retroactively documenting the frozen legacy
  layer in detail — ADR-018 through ADR-020 already serve as its
  documentation of record.

## Alternatives rejected

**Option 1** was rejected as a restatement of the status quo that produced
duplicate, competing documentation.

**Option 3** was rejected because a mirrored root summary would drift from
`platform/docs/` the same way the root's stub JSON "registries" drifted
from reality — a second copy is a maintenance liability, not a safeguard.
