# ADR-019 — `platform/` Extension Policy

- **Status:** Accepted
- **Date:** 2026-08-06
- **Implements:** GADR-002 (STARCORE Architecture Governance Report)

## Context

ADR-018 established `platform/` as the sole authoritative body of the
repository. That boundary is only useful if new work actually lands inside
it. The discovery audit found that nearly every capability STARCORE's
root-level scaffolding claims to provide (Proxmox control, AI inference,
distributed agents, CLI, registries) already has a real, tested
implementation inside `platform/` — and that the root-level versions arose
specifically because new functionality was, historically, added as a new
top-level directory rather than as an extension of the existing product.
Without an explicit extension policy, that pattern will repeat.

## Options

1. **No explicit policy** — rely on ADR-018 alone and trust future sessions
   to infer where new code belongs.
2. **Explicit extension policy**: all new STARCORE functionality is added
   inside `platform/`, using its existing contracts (`BaseProvider`,
   `AIProvider`, the plugin system) and its existing ADR + CI process; no
   new top-level directories are created at the repository root for
   production code.
3. **Two-tier policy** — allow new top-level directories for
   "experimental" work with a lighter process, formalizing into
   `platform/` later.

## Decision

**Option 2.** Every new feature, provider, or automation capability is
implemented inside `platform/packages/` or `platform/apps/`, following the
existing contracts documented in `platform/CLAUDE.md` (provider SDK,
pluggable `AIProvider`, plugin system), and passes through the existing ADR
process (`docs/adr/ADR-0NN-*.md`) before or alongside implementation. No new
top-level directory is created at the repository root for production
functionality.

## Consequences

- A new infrastructure provider (e.g. a hypothetical mobile/edge
  connector) is added as `platform/packages/providers/<name>/` implementing
  `BaseProvider`, not as a new root-level `<name>/` directory.
- A new AI capability extends `platform/packages/ai/`'s `AIProvider`
  abstraction (ADR-007), not a new `ai_*` root module.
- All new code is subject to the existing CI gate (ruff, pyright, bandit,
  pip-audit, pytest at 100% coverage, alembic check, mkdocs --strict) by
  virtue of living inside `platform/`'s existing tooling scope — there is
  no way to add untested, unreviewed code without it being visible in the
  same gate that already protects the product.
- This does not forbid work adjacent to `platform/` in principle (see
  ADR-024 for the Android/Termux Edge Node, which is explicitly kept
  *outside* `platform/` by design) — it forbids *unreviewed scaffolding
  that duplicates functionality `platform/` already owns*.

## Alternatives rejected

**Option 1** was rejected because the discovery audit is direct evidence
that "trust future sessions to infer this" already failed, repeatedly,
across roughly 49 commits.

**Option 3** was rejected because "experimental first, formalize later" is
exactly the pattern that produced `autonomous/`, `distributed/`, `ai_core/`,
and friends — none of which were ever formalized. A lighter process for new
top-level directories reproduces the same failure mode with a documented
excuse attached.
