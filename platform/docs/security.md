# Security

This page indexes STARCORE's security-relevant design decisions and where
to find the detail behind each. For the vulnerability-reporting process,
see [`SECURITY.md`](https://github.com/Fatalerorr69/starcore-platform/blob/main/SECURITY.md)
at the repository root (not part of this documentation site, since GitHub
surfaces it directly under the repo's Security tab).

## Authentication

A single static shared `X-API-Key`, compared in constant time
(`hmac.compare_digest`), protects every route except `/`, `/health`,
`/ui`, and static UI assets. The server fails closed (`503`) if no key is
configured. See [ADR-012](adr/ADR-012-api-authentication-model.md) and
[API Reference](api.md#authentication).

## Rate limiting

Per-IP request limiting via `slowapi`, configurable with
`STARCORE_RATE_LIMIT_PER_MINUTE` (`0` disables it), applied to every route
except `/health`. See [ADR-003](adr/ADR-003-rate-limiting.md).

## Secret redaction

`packages/core/security.py` centralizes secret handling so no endpoint
needs its own masking logic:

- `redact_database_url()` masks credentials embedded in
  `STARCORE_DATABASE_URL` before it can reach `/health` or `/diagnostics`.
- `scrub_configured_secrets()` strips any currently-configured secret
  (API key, Proxmox token, AI provider keys) found verbatim in a string —
  applied to provider connection-failure messages before they're logged or
  returned, since third-party SDK exceptions are not otherwise guaranteed
  not to echo connection details.

`tests/test_security.py` includes a regression sweep that configures a
synthetic database password and asserts it never appears in any
unauthenticated response body.

## Plugin trust boundary

Plugins execute arbitrary Python at import time with the full privileges
of the STARCORE process — there is no sandboxing. See
[Plugins → Trust model](plugins.md#trust-model) and
[ADR-011](adr/ADR-011-plugin-trust-boundary.md).

## Dependency-failure safety

`depends_on` is a success gate: a resource whose declared dependency did
not succeed is never handed to a provider, so a partially-failed blueprint
run cannot silently continue building on top of a broken prerequisite. See
[ADR-010](adr/ADR-010-dependency-failure-semantics.md).

## Supply chain / CI gates

Every PR runs `pip-audit` (dependency vulnerabilities), Bandit (SAST), and
gitleaks (secret scanning) as blocking gates, plus a nightly independent
rerun of all three. See [ADR-008](adr/ADR-008-ci-security-gates.md) and
[ADR-004](adr/ADR-004-dependency-vulnerability-scanning.md).

## Provider credentials

Docker and Proxmox credentials are supplied via environment/`.env` only,
never committed (`.env` is gitignored), never logged, and — for Proxmox —
scrubbed from any exception text that reaches a response body or a log
line (see [Secret redaction](#secret-redaction) above). A provider
instance is a long-lived singleton reused across every task targeting it;
`connect()` is guarded by a per-instance `asyncio.Lock` so concurrent
scheduler-wave calls establish the connection at most once — see
[ADR-002](adr/ADR-002-provider-lifecycle.md). `execute()` itself is not
rate-limited across a wave; see
[ADR-013](adr/ADR-013-provider-concurrency-policy.md) for why, and the
concrete conditions that would change that.

## Container

The Docker image runs as a dedicated non-root user with a `HEALTHCHECK`
against `GET /health`.

## Known, accepted limitations

Also listed in `SECURITY.md`: no per-user identity or RBAC (single shared
key, targeting single-operator/small-team homelab deployments), no
sandboxing for plugins, and providers run with whatever credentials you
configure — protect the API key and prefer trusted-network exposure.
