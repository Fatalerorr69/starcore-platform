# ADR-017 — Plugin Operator Controls

- **Status:** Accepted
- **Date:** 2026-08-05
- **Implements:** REC-009

## Context

ADR-011 established that STARCORE's plugin system has no sandboxing:
`importlib.import_module()` executes a plugin's top-level code in-process
with full process privileges. ADR-011's response was documentation — state
the trust model honestly and leave the deployment decision to the operator.

That was the right call for a first sprint, but it left a gap: an operator
who *understood* the trust model and wanted to deploy STARCORE with only a
specific subset of plugins active (or with plugins disabled entirely) had no
mechanism to express that preference without manually removing directories
from `plugins/`. The only available controls were filesystem-level, meaning
they had to be applied *outside* the process, could not be version-controlled
as part of the deployment configuration, and were irreversible during a
running session.

This gap matters in two concrete scenarios:

1. **Staged rollout**: an operator adds a new plugin to the codebase but wants
   to gate it behind an environment variable before enabling it in production.
2. **Defense in depth**: an operator deploys STARCORE in an environment where
   `plugins/` is writable by a less-trusted party (a shared volume, a CI
   runner that clones the repo). Even though ADR-011 documents that this is
   unsafe, the operator may not be able to prevent the filesystem condition —
   but they can prevent `load_all()` from acting on it.

## Options

1. **`STARCORE_PLUGINS_ENABLED` kill switch only** — boolean env var that
   disables all plugin loading when false. Simple, binary, no partial control.

2. **`STARCORE_PLUGINS_ENABLED` + `STARCORE_PLUGINS_ALLOWLIST`** — kill
   switch plus a comma-separated allowlist of plugin names. When the allowlist
   is non-empty, only named plugins may load; any discovered plugin not on the
   list is skipped with a logged warning. The kill switch is a special case:
   `plugins_enabled=false` short-circuits before the allowlist is consulted.

3. **Cryptographic signing** — require plugins to ship a signature file
   (`.starcore-plugin-sig`) signed by a trusted key managed by the operator.
   Only plugins whose signature verifies are loaded.

4. **Subprocess isolation** — run each plugin in a subprocess with a
   capability-scoped IPC channel instead of importing it in-process.

## Decision

**Option 2.** It addresses both concrete scenarios with minimal code and
no new infrastructure:

- The kill switch covers deployments that want an unconditional "no plugins"
  guarantee without filesystem manipulation.
- The allowlist covers staged rollout and defense-in-depth without requiring
  cryptographic infrastructure the project doesn't otherwise need.
- Both controls are environment-variable-driven, making them compatible with
  Docker Compose, Kubernetes ConfigMaps, `.env` files, and CI pipelines — the
  same deployment tooling STARCORE already uses for all other settings.

Options 3 and 4 are rejected as disproportionate to the current threat model
(see *Alternatives rejected* below).

## Implementation

Two fields added to `Settings` in `packages/core/config.py`:

```python
plugins_enabled: bool = True
plugins_allowlist: str = ""  # comma-separated; empty = allow all
```

`PluginManager.load_all()` in `packages/core/plugin_manager.py` evaluates
these at the start of every call:

1. If `plugins_enabled` is `False`, return `[]` immediately and log an
   info message. No module is imported.
2. Build an allowlist set by splitting `plugins_allowlist` on commas and
   stripping whitespace. An empty set means no restriction.
3. For each discovered plugin name: if the allowlist set is non-empty and
   the name is absent, skip with a logged warning and continue to the next.
4. Otherwise, import and register as before.

The existing behavior (all plugins load) is preserved exactly when both
settings are at their defaults (`plugins_enabled=true`, `plugins_allowlist=""`).

## Consequences

- **No behavior change at the defaults.** Existing deployments are unaffected.
- Operators can now express plugin policy declaratively, in the same
  configuration layer as every other STARCORE setting.
- The allowlist operates on *plugin directory names*, not module paths or
  hashes. It prevents `importlib.import_module()` from being called for
  unlisted plugins — but a plugin that is on the list still runs with full
  process privileges (ADR-011's trust model is unchanged).
- These controls are not a substitute for filesystem access control. An
  operator who cannot trust `plugins/` should also restrict who can write to
  it; the allowlist adds a second layer, not a replacement for the first.
- ADR-011 option 3 ("signing/allow-listing") is now partially realized as a
  name-based allowlist. Cryptographic signing remains available as a future
  upgrade if a concrete scenario requires it.

## Alternatives rejected

**Option 3 (cryptographic signing):** adds key management, a signing workflow
for plugin authors, and signature verification logic — all for a project where
every deployed plugin is currently first-party code authored and reviewed by
the same operator. This addresses a third-party plugin distribution threat
model STARCORE does not currently have.

**Option 4 (subprocess isolation):** eliminates the in-process execution risk
entirely but requires a stable IPC protocol, a serialization boundary for
`ProviderRegistry` and `EventBus` interactions, and a mechanism to return
results (registered providers, event subscriptions) across a process boundary.
The complexity is high relative to the benefit for a modular monolith in a
single-operator homelab context. If a real multi-tenant deployment scenario
emerges that requires genuinely untrusted plugin execution, this ADR should be
revisited — but speculative infrastructure for a demonstrated need is exactly
what ADR-011 argued against, and this ADR maintains that principle.
