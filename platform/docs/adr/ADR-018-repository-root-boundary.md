# ADR-018 — Repository Root vs. `platform/` Boundary

- **Status:** Accepted
- **Date:** 2026-08-06
- **Implements:** GADR-001 (STARCORE Architecture Governance Report)

## Context

A repository-wide discovery audit (STARCORE SAEF Integration Discovery Report,
2026-08-06) found that `starcore-platform` contains two structurally
unrelated bodies of content:

1. `platform/` — the actual STARCORE Platform product (Proxmox/Docker
   orchestration). Added in a single commit, carries 601 tests, 100%
   coverage, a full CI gate, 17 ADRs, and its own cross-session knowledge
   layer (`.starcore/`).
2. Everything else at the repository root — 65 Termux/Android install
   scripts, 411 statically-generated JSON files under `runtime/`, and
   dozens of Python modules (`autonomous/`, `distributed/`, `ai_core/`,
   `knowledge/`, etc.) averaging 14-20 lines each, whose entire behavior is
   writing a fixed `{"status": "ready"}`-shaped JSON blob. None of this
   content has tests, is exercised by CI, or is imported by `platform/`.

Git history confirms the asymmetry: 49 of the repository's 50 commits touch
only the root-level content; exactly one commit added the entirety of
`platform/`. Without an explicit boundary, future sessions risk treating
root-level scaffolding as authoritative, extending it further, or drawing
conclusions from its fabricated "status: ready" data.

## Options

1. **No boundary — treat the whole repository as one undifferentiated
   codebase.** Status quo. Leaves the ambiguity in place.
2. **Declare `platform/` the sole authoritative source; root content is
   non-authoritative until explicitly re-classified.** Matches what the
   discovery audit already found to be true in practice.
3. **Immediately delete root-level content.** Removes the ambiguity but is
   destructive and pre-empts a decision (e.g. Android/Termux strategy,
   ADR-024) that has not yet been made for every subtree.

## Decision

**Option 2.** `platform/` is the single source of truth for code,
configuration, and runtime behavior. Content outside `platform/` carries no
architectural authority: it must not be assumed functional, must not be
extended, and must not be used as a basis for decisions about the product's
actual capabilities, unless and until a specific subtree is explicitly
re-classified by a follow-up ADR (see ADR-020, ADR-024).

## Consequences

- Any claim about system capability ("Proxmox connector exists", "agent
  fabric is active") must be verified against `platform/`, never against
  root-level JSON registries or install scripts — those are historical
  artifacts, not live state.
- New sessions reading `platform/CLAUDE.md` get accurate cold-start context
  without needing to re-discover this boundary each time (this ADR is the
  durable record).
- This ADR does not itself move, archive, or delete anything — it only
  establishes the authority boundary. Disposition of the non-authoritative
  content is handled by ADR-020 (freeze) and, for the Android/Termux
  subtree specifically, ADR-024.

## Alternatives rejected

**Option 1** was rejected because it is the status quo that produced the
ambiguity this ADR exists to resolve — restating it changes nothing.

**Option 3** was rejected as premature: deleting content before every
subtree has an explicit disposition decision (in particular, before the
Android/Termux question is resolved per ADR-024) risks discarding a
component the repository owner still intends to use in some form.
