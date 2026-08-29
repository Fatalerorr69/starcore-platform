# STARCORE Edge Node — Architecture

## Purpose

Details the STARCORE Edge Node concept decided in ADR-024: a standalone
Android/Termux agent providing mobile diagnostics, OSINT collection,
remote management, and general data collection, architecturally separate
from `platform/`'s core runtime. This document elaborates the shape of
that architecture without deciding its unresolved questions — those are
listed explicitly in "Open Questions" and remain open until a dedicated
follow-up ADR resolves each one.

## Scope

In scope: the relationship between an Edge Node and `platform/`'s
existing HTTP API, the responsibilities an Edge Node may take on, and the
constraints it must respect (ADR-012, ADR-018, ADR-019).

Out of scope, deliberately: any new API endpoint contract, any change to
the authentication model beyond what ADR-012 already defines, and any
decision about where Edge Node code physically lives. These are the three
open questions ADR-024 raised and this document does not close them.

## Architecture Overview

```text
Edge Node (Android/Termux)                    STARCORE Core (platform/)
+---------------------------+                 +---------------------------+
| mobile diagnostics        |--HTTPS + auth-->| existing FastAPI API      |
| OSINT collection          |--HTTPS + auth-->| (packages/core)           |
| remote management trigger |--HTTPS + auth-->|                           |
| local cache / queue       |                 | ProviderRegistry, Sched-  |
+---------------------------+                 | uler, EventBus (in-proc, |
                                               | not reachable by Edge     |
                                               | Node directly)            |
                                               +---------------------------+
```

The Edge Node is, from `platform/`'s point of view, an HTTP client like
any other — no different code path, no special-cased trust.

## Edge Node Responsibilities

- Collect local device/environment signals (mobile diagnostics).
- Collect OSINT data from sources reachable to the device.
- Trigger existing `platform/` operations on request (remote management)
  by calling existing endpoints — it does not gain new server-side
  capability by existing.
- Queue/cache data locally when connectivity to `platform/` is
  unavailable, and forward it once reachable.

The Edge Node does **not**: hold a copy of `ProviderRegistry` state,
participate in `EventBus` dispatch, access the SQLite/Alembic-managed
database directly, or execute blueprint tasks itself.

## Communication Boundaries

All interaction crosses `platform/`'s existing HTTP API surface (see
`CLAUDE.md`, "API endpoints"). No new transport (e.g. a direct SSH/gRPC
channel into `platform/`'s process) is introduced by this document. If a
future need requires one, it is a new ADR, not an extension of this
architecture.

## Authentication and Trust Boundary

Today, the only authentication mechanism `platform/` has is the single
shared `X-API-Key` (ADR-012). An Edge Node using that mechanism as-is
would hold the same credential as every other API client — acceptable for
a single-operator homelab, but a real design trade-off for a device that
can be lost or stolen. Whether Edge Node authentication should:

- reuse the existing shared key as-is, or
- require a new, narrower-scoped credential type

is **not decided here** — see Open Questions. This document does not
modify ADR-012.

## Data Flow

```text
Device sensor / OSINT source
        |
        v
Edge Node (local processing, local cache)
        |
        v  (HTTPS, authenticated, when connectivity available)
platform/ API endpoint (existing or, if approved later, new)
        |
        v
Existing platform/ persistence (SQLite/Alembic) or provider action
```

Exact payload shape and the specific endpoint(s) involved are open
(see Open Questions) — this diagram shows the direction and trust
boundary, not a wire format.

## Deployment Model

The Edge Node runs on the operator's own Android/Termux device, entirely
independent of `platform/`'s deployment (Docker Compose, bare `uvicorn`,
etc. — see `docs/installation.md`). It has its own lifecycle: it can be
installed, updated, or uninstalled without touching `platform/` at all,
and vice versa.

## Security Considerations

- A lost/stolen device carrying Edge Node credentials is a real risk not
  present for a server-side-only deployment — this is the primary reason
  the "reuse shared key vs. scoped credential" question (below) is not
  waved through as settled.
- The Edge Node must not be granted any capability `platform/`'s existing
  API doesn't already gate behind authentication (ADR-012) — it is a
  client, not a trusted extension of the server.
- Any future endpoint built for Edge Node use (e.g. an OSINT/diagnostics
  ingestion endpoint) goes through the same CI security gates as every
  other endpoint (bandit, gitleaks, rate limiting) per ADR-019's extension
  policy — no exception is created for "Edge Node-only" code paths.

## Open Questions

These are unresolved by ADR-024 and remain unresolved by this document.
Each requires its own follow-up ADR before implementation:

1. **Endpoint for OSINT/diagnostics ingestion** — does the Edge Node need
   a new server-side endpoint (e.g. `POST /edge/report`), or can existing
   endpoints (`POST /resources/action`, `GET /diagnostics`) cover the
   initial use case?
2. **Authentication scoping** — shared `X-API-Key` (ADR-012, as-is) vs. a
   new, narrower-scoped credential type for Edge Node clients specifically.
3. **Code location** — a new directory in `starcore-platform` kept
   outside `platform/` (per ADR-018/019), or a fully separate repository.

## Relation to ADR-024

This document is the "architecture detail" reference that ADR-024 points
to. It does not supersede, amend, or add decisions to ADR-024 — it only
expands the shape of the architecture ADR-024 already decided, and makes
explicit which parts of that shape are still open. Resolving any Open
Question above requires its own ADR, not an edit to this file that quietly
turns an open question into a decision.
