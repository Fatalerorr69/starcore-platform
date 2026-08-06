# ADR-024 — Android/Termux as an Edge Node, Outside Core Runtime

- **Status:** Accepted
- **Date:** 2026-08-06
- **Implements:** GADR-004 (STARCORE Architecture Governance Report, revised)
- **Relates to:** ADR-012 (API Authentication Model), ADR-018

## Context

The repository's legacy root layer includes an extensive Android/Termux
subtree (`plugins/enabled/android/`, `installers/android/`,
`runtime/android/`, and related install scripts) with no relationship to
`platform/`'s actual product (a Proxmox/Docker orchestrator with a FastAPI
backend and a static web dashboard at `GET /ui`). Per ADR-020 this subtree
is currently frozen along with the rest of the legacy layer. Its owner has
indicated a real intended use — mobile diagnostics, OSINT collection,
remote management, and data collection — rather than abandonment, which
this ADR addresses as a forward-looking architecture rather than leaving it
solely as frozen legacy.

## Options

1. **Reintegrate into `platform/` core runtime** — bring Android/Termux
   code inside `platform/packages/`.
2. **Independent Edge Node** — a separate, loosely-coupled client that
   talks to `platform/`'s existing HTTP API (`X-API-Key` per ADR-012); no
   shared code, memory, or process with `platform/`.
3. **Thin client only** — rely entirely on the existing `GET /ui` dashboard
   in a mobile browser; no dedicated Android/Termux agent at all.

## Decision

**Option 2 — STARCORE Edge Node Architecture.** Android/Termux becomes a
standalone Edge Node agent, architecturally and physically separate from
`platform/`'s core runtime, communicating exclusively over `platform/`'s
existing authenticated HTTP API. It is responsible for:

- mobile diagnostics (device/environment data collected at the edge),
- OSINT data collection,
- remote management (triggering existing `platform/` operations such as
  `POST /resources/action` or `POST /blueprints/run`),
- general data collection and forwarding.

The Edge Node holds no core runtime logic, no direct database access, and
no in-process coupling to `platform/`'s `EventBus`, `ProviderRegistry`, or
scheduler. Per ADR-018/ADR-019, its code does not live inside
`platform/packages/`.

## Consequences

- `platform/`'s API surface, security model (ADR-012), and provider
  contracts are unaffected — the Edge Node is, from `platform/`'s
  perspective, just another authenticated API client.
- Any new server-side capability the Edge Node needs (e.g. an endpoint to
  receive OSINT/diagnostic payloads) requires its own ADR and
  implementation inside `platform/packages/core`, following ADR-019 — this
  ADR authorizes the *architecture*, not any specific new endpoint, which
  remains an open design question (see `docs/architecture/edge-node.md`).
- The existing `plugins/enabled/android/`, `installers/android/`, and
  `runtime/android/` code is **not** reused as the Edge Node's
  implementation — per the discovery audit, it contains no functional
  logic (stub JSON writers only) and remains frozen legacy under ADR-020.
  The Edge Node, when built, is a new implementation guided by this ADR's
  architecture, not a resurrection of the frozen code.
- Where the Edge Node's implementation is hosted (a new directory in this
  repository, kept outside `platform/`, versus a separate repository) is
  left open and does not need to be decided by this ADR.

## Alternatives rejected

**Option 1** was rejected because it would pull an Android/Termux runtime
dependency into a product whose core value (per `platform/README.md`) is a
Proxmox/Docker orchestrator with no such dependency today — violating
ADR-019's principle of not duplicating or entangling unrelated concerns
inside `platform/`.

**Option 3** was rejected because it does not address the stated use cases
(OSINT collection, background diagnostics, data collection) that a passive
browser dashboard cannot perform — these require an active agent running
on the device, not just a viewer of `platform/`'s existing UI.
