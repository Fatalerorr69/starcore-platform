# ADR-023 — SAEF as a Workflow Protocol, Not a System

- **Status:** Accepted
- **Date:** 2026-08-06
- **Implements:** GADR-007 (STARCORE Architecture Governance Report)

## Context

A "STARCORE AI Engineering Framework (SAEF)" bootstrap prompt was submitted
proposing a new, parallel operating framework — its own execution modes
(Discovery/Planning/Implementation/Review/Optimization), its own registries
(project/module/service/technology/documentation/decision/risk), and its
own Czech-language reporting format. Analysis (the SAEF Integration
Discovery Report) found that `platform/.starcore/` already implements
equivalent capability: a Decision Engine with mandated report sections
(`memory/decision_engine.md`), a session ledger (`sessions/ledger.yaml`),
a prompt registry (`prompts/registry.yaml`), and QC engines (regression
sentinel, release readiness, impact analyzer) — all tested, all already in
active use per `CLAUDE.md`. Adopting SAEF as a second, parallel system
would duplicate this rather than extend it.

## Options

1. **Adopt SAEF as proposed** — a new, standalone framework alongside
   `.starcore/`.
2. **Reject SAEF entirely** — no further action on the prompt.
3. **Treat SAEF as a workflow protocol layered onto `.starcore/`** — its
   useful ideas (phase-gated execution modes, structured Czech reporting,
   decision tables) are absorbed into the existing Decision Engine and
   prompt registry; no new runtime, registry, or reporting mechanism is
   built.

## Decision

**Option 3.** SAEF does not become a system. Its phase-gated execution
modes (DISCOVERY / PLANNING / IMPLEMENTATION / REVIEW / OPTIMIZATION) are
recognized as compatible with — and are executed through — the existing
Decision Engine format already mandated by `platform/CLAUDE.md`
(STAV / CO BYLO ZJIŠTĚNO / CO BYLO OVĚŘENO / RIZIKA / DOPORUČENÍ / DOPAD /
RIZIKO / ROLLBACK / DALŠÍ KROK). Each SAEF-style prompt received in a
session is logged as an entry in `platform/.starcore/prompts/registry.yaml`
(see PROM-009 through PROM-012) rather than triggering a new framework
bootstrap.

## Consequences

- Future prompts proposing a new "framework," "engine," or "operating
  system" for STARCORE are evaluated against this ADR first: do they
  request a capability `.starcore/` cannot already express? If not, they
  are registered as a prompt/workflow, not implemented as new
  infrastructure.
- This ADR, together with ADR-018/019, gives a standing answer to the
  recurring pattern observed in this repository's history (bootstrap-style
  prompts proposing parallel systems) without needing to re-litigate it
  each time.
- No code changes result directly from this ADR; its effect is procedural.

## Alternatives rejected

**Option 1** was rejected for the same reason as the root-level legacy
scaffolding exists in the first place: parallel systems accumulate faster
than they get reconciled.

**Option 2** was rejected because SAEF's phase-gated structure and
Czech-language reporting discipline are genuinely compatible with —
and reinforce — the existing Decision Engine; outright rejection would
discard a usable framing rather than integrating it.
