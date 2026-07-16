# Security Policy

## Supported versions

STARCORE Platform is pre-alpha (`0.1.0-dev`). Only the current `main`
branch receives fixes; there are no maintained release lines yet.

## Reporting a vulnerability

Please report suspected vulnerabilities **privately** via
[GitHub Security Advisories](https://github.com/Fatalerorr69/starcore-platform/security/advisories/new)
("Report a vulnerability"). Do not open a public issue for security
reports.

Include what you can: affected component/endpoint, reproduction steps,
impact assessment, and any suggested fix. You can expect an initial
response within a reasonable time frame for a single-maintainer project;
please allow time for a fix before public disclosure.

## Security model (current state)

- **Authentication:** single static shared API key (`X-API-Key` header),
  compared in constant time (`hmac.compare_digest`). The API fails closed
  (HTTP 503) when no key is configured. There is no per-user identity,
  RBAC, or multi-tenancy — the platform targets single-operator homelab
  deployments.
- **Rate limiting:** per-IP, configurable via
  `STARCORE_RATE_LIMIT_PER_MINUTE` (default 60/min; `/health` exempt).
- **Secrets:** all credentials (API key, Proxmox token, Anthropic key)
  are supplied via environment/`.env` only; `.env` is gitignored and
  never logged.
- **Dependencies:** `pip-audit` runs as a blocking CI gate on every PR;
  Dependabot keeps versions fresh; GitHub security alerts are enabled.
- **Container:** the Docker image runs as a dedicated non-root user.

## Known limitations (accepted for the current scope)

- Plugins run in-process with full application privileges (no
  sandboxing). Only install plugins you trust.
- Providers run in-process with the credentials you configure; the
  platform can create and destroy real infrastructure — protect the API
  key accordingly and prefer trusted-network exposure.
