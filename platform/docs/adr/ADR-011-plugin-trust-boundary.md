# ADR-011 — Plugin Trust Boundary

- **Status:** Accepted (documents existing, unchanged behavior)
- **Date:** 2026-07-26

## Context

STARCORE's plugin system (`packages/core/plugin_manager.py`) discovers
directories under `plugins/` and imports them via
`importlib.import_module()`, then calls a `register(context)` function the
module is expected to expose. This mechanism was implemented early in the
project and works correctly, but no design document stated explicitly what
security boundary — if any — exists between a loaded plugin and the
STARCORE process itself. An operator reading only the plugin *contract*
(`context.registry`, `context.events`) could reasonably assume those two
objects are the full extent of what a plugin can touch.

## Problem

They are not. `importlib.import_module()` executes a plugin's top-level
module code immediately, in-process, before `register()` is even looked
up. This is standard Python import behavior, not something STARCORE's
plugin loader adds or could easily remove without a fundamentally
different mechanism (subprocess isolation, a restricted interpreter,
capability-scoped context objects). Leaving this undocumented risked an
operator placing a lower-trust plugin under `plugins/` on the assumption
that `context.registry`/`context.events` was an enforced sandbox rather
than a suggested API surface.

## Options

1. **Document the boundary as it exists (chosen):** state plainly that
   plugins run with full process privileges and are not sandboxed, and
   that deployment decisions must treat `plugins/` accordingly.
2. **Build real isolation:** run plugin code in a subprocess or restricted
   interpreter, passing it a capability-scoped proxy instead of the live
   `ProviderRegistry`/`EventBus`.
3. **Restrict plugin loading to a signed/allow-listed set.**

## Decision

Option 1 for this sprint. `docs/plugins.md` now states the trust model
explicitly: a plugin must be trusted to the same degree as the STARCORE
codebase itself, because loading one *is* granting it that degree of
trust, whether or not the plugin author intended to use more than
`context.registry`/`context.events`. No code changed — `load_all()`'s
behavior (on-demand only, triggered by an authenticated `GET /plugins` or
local `starcore plugins`, never automatic at process startup) was already
a reasonable containment of *when* plugin code runs; what was missing was
being honest about *what* it can do once it runs.

## Consequences

- No behavior change. This ADR is a documentation decision: `docs/plugins.md`
  is the source of truth for the trust model, cross-linked from
  `docs/architecture.md`.
- Operators deploying STARCORE in any environment where `plugins/` could
  be writable by a less-trusted party (shared host, mounted volume another
  process can write to, multi-tenant environment) now have an explicit,
  unambiguous statement that doing so is equivalent to granting that party
  STARCORE's own credentials and network access.
- Options 2 and 3 remain available as future work if a real deployment
  scenario requires running genuinely untrusted plugin code; this ADR
  deliberately does not attempt that now, since no such requirement has
  been demonstrated (the project's own guidance is to prefer a small
  verified change over speculative infrastructure).

## Alternatives rejected

Option 2 (real isolation) is significant new infrastructure with no
demonstrated current need — STARCORE is a modular monolith for a
single-operator or small-team homelab context, and the two shipped example
plugins (`example_provider`, `run_logger`) are exactly the kind of
first-party, operator-authored code the current model is designed for.
Option 3 (signing/allow-listing) adds a distribution and trust-management
problem STARCORE does not otherwise have, for a threat model (accepting
plugins from parties you don't otherwise trust) the project does not
currently target.
