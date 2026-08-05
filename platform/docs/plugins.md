# Plugin System

STARCORE's plugin mechanism lets you register a custom `BaseProvider`
implementation or subscribe to blueprint-execution events without modifying
`packages/`. It is intentionally simple: a plugin is a Python package that
exposes one function, `register(context)`. There is no sandboxing, no
permission model, and no isolation between a plugin and the STARCORE
process itself — see [Trust model](#trust-model) before deploying any
plugin you did not write.

## Discovery

`PluginManager.discover()` (`packages/core/plugin_manager.py`) lists every
direct subdirectory of `plugins/` that contains an `__init__.py`. Nothing
else about a candidate directory is inspected before it is treated as a
plugin — a valid Python package layout is the only requirement.

## Import and registration

`PluginManager.load_all()`:

1. Adds the parent of `plugins/` to `sys.path` (once, if not already
   present).
2. For each discovered plugin, calls `importlib.import_module("plugins.<name>")`.
3. Looks up a module-level `register` attribute. If absent, the plugin is
   skipped with a warning — it does not fail the whole load.
4. Calls `register(context)`, where `context` is a `PluginContext` exposing:
   - `context.registry` — the global `ProviderRegistry`, for adding custom
     `BaseProvider` implementations (see `plugins/example_provider/`).
   - `context.events` — the global `EventBus`, for subscribing to
     `task.started`, `task.completed`, `run.completed` (see
     `plugins/run_logger/`).
5. On success, the plugin is recorded so a second `load_all()` call in the
   same process does not import or `register()` it again.

Plugin loading is **on-demand, not automatic at process startup**: nothing
in `packages/core/main.py`'s FastAPI app construction or `apps/cli/main.py`
calls `load_all()` unconditionally. It runs only when an operator or an
authenticated API caller explicitly triggers it — the `starcore plugins`
CLI command, or `GET /plugins` (behind `verify_api_key`).

## Failure handling

- **Import failure** (`ImportError`): logged, that plugin is skipped, the
  rest of `plugins/` still loads.
- **Missing `register()`**: logged as a warning, skipped.
- **Exception inside `register()`**: caught and logged
  (`logger.exception`), that plugin is skipped, the rest of `plugins/`
  still loads.

A single broken plugin cannot prevent the others from loading, but it also
cannot be partially loaded — either its `register()` call completes, or the
plugin is treated as entirely absent.

## Trust model

**Plugins are not sandboxed.** `importlib.import_module()` executes a
plugin's `__init__.py` top-level code immediately, in-process, with the
full privileges of the STARCORE process — before `register()` is even
looked up. This is inherent to Python's import system, not a STARCORE
design choice, and there is currently no mechanism (subprocess isolation,
restricted execution, capability limits) that changes this.

**Consequence:** a plugin must be trusted to exactly the same degree as the
STARCORE codebase itself. A plugin can read `STARCORE_*` environment
variables, call any provider's credentials, read or write any file the
process can reach, and make arbitrary network calls — nothing in the
plugin contract restricts it to `context.registry` and `context.events`;
those are just the *intended* extension points, not an enforced boundary.

**Deployment implications:**

- Only place plugins you wrote yourself, or have fully code-reviewed, under
  `plugins/`.
- In any deployment where `plugins/` could be writable by a party less
  trusted than whoever operates STARCORE itself (a shared host, a mounted
  volume another process can write to, a multi-tenant environment), treat
  that as equivalent to giving that party STARCORE's own credentials and
  network access — because loading a plugin from that directory does
  exactly that.
- `GET /plugins` and `starcore plugins` are gated the same way as every
  other privileged operation (API key / local operator access) precisely
  because triggering plugin load is a privileged, code-executing action,
  not a read-only listing.

If you need to run untrusted or third-party plugin code, that requires
infrastructure this project does not currently provide (a subprocess or
container boundary, a restricted API surface passed to `register()` instead
of the live `ProviderRegistry`/`EventBus`) — do not assume isolation that
does not exist.

## Operator controls

Two settings let an operator restrict which plugins load, without modifying
`plugins/` or the codebase.

### `STARCORE_PLUGINS_ENABLED`

Boolean (default `true`). When set to `false`, `load_all()` returns
immediately without importing or registering any plugin:

```bash
STARCORE_PLUGINS_ENABLED=false
```

Use this to disable all plugin loading in environments where no plugins
are deployed, or where you want to guarantee that `plugins/` cannot execute
even if its contents change.

### `STARCORE_PLUGINS_ALLOWLIST`

Comma-separated list of plugin names (default `""` — empty means *allow
all*). When non-empty, any discovered plugin whose name is **not** in the
list is skipped with a warning:

```bash
STARCORE_PLUGINS_ALLOWLIST=run_logger,my_custom_provider
```

Leading and trailing whitespace around each name is trimmed. An empty
string (the default) disables the allowlist — all discovered plugins are
eligible to load (subject to `STARCORE_PLUGINS_ENABLED`).

**Note:** these controls restrict *which* plugins are loaded, not *what*
a loaded plugin can do. A plugin on the allowlist still runs with the full
privileges of the STARCORE process — the trust model documented above
still applies.

## Writing a plugin

See `plugins/example_provider/` (registers a custom provider) and
`plugins/run_logger/` (subscribes to `run.completed`) for minimal, complete
examples. Both follow the same shape:

```python
def register(context) -> None:
    # add a provider:
    context.registry.register(MyProvider())
    # and/or subscribe to events:
    context.events.subscribe("run.completed", my_handler)
```
