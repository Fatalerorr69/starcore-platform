# ADR-012 — API Authentication Model

- **Status:** Amended (REC-001, 2026-08-05 — RBAC/JWT layer added; original
  single-key decision remains intact as the legacy path)
- **Date:** 2026-07-26 (ADR written); original underlying decision dated 2026-07-16;
  amended 2026-08-05 to reflect REC-001 changes

## Context

STARCORE is a modular monolith aimed at homelab/self-hosted deployments,
typically operated by one person or a small trusted team. The original model
(Sprint 003, PR #38) protected every route with a single shared `X-API-Key`
secret. As deployments grow to involve automation scripts, dashboards, and
occasionally more than one human operator, the lack of any role distinction
became a pain point: every client that needed read access also had write access.
REC-001 adds a proper RBAC/JWT authentication layer while keeping the existing
`X-API-Key` path fully intact so existing deployments are not broken.

## Decision

### Original model (unchanged, now the "legacy path")

A single `STARCORE_API_KEY` value, supplied via the `X-API-Key` request
header, is accepted on all protected routes and maps to the `admin` role.

- **Fails closed:** if `STARCORE_API_KEY` is not configured, every route
  that checks it returns `503`.
- **Constant-time comparison:** `hmac.compare_digest` prevents timing attacks.
- **Backward compatible:** existing deployments with only `STARCORE_API_KEY`
  set continue to work without any configuration change.

### New model — RBAC / JWT (REC-001)

When `STARCORE_JWT_SECRET_KEY` is configured, clients may authenticate via
`Authorization: Bearer <token>`. The system supports three roles:

| Role | Weight | Capabilities |
|------|--------|--------------|
| `reader` | 0 | Read-only endpoints (`/providers`, `/runs`, `/plugins`) |
| `operator` | 1 | All reader endpoints plus blueprint execution, diagnostics, AI generation |
| `admin` | 2 | All endpoints including user management (`/auth/users`) |

`require_role(minimum_role)` is a FastAPI dependency factory used at the router
or endpoint level; it resolves the caller via `get_current_user()`, which tries
Bearer JWT first and falls back to `X-API-Key`.

Token endpoints:
- `POST /auth/token` — password-based login; returns a short-lived access JWT
  (default 30 min) and a long-lived refresh JWT (default 7 days).
- `POST /auth/refresh` — exchange a refresh token for a new access token.
- `POST /auth/users` (admin) — create a user.
- `GET /auth/users` (admin) — list users.

Passwords are stored as bcrypt hashes (`bcrypt.gensalt()`). JWTs are HS256,
signed with `STARCORE_JWT_SECRET_KEY`. Token payloads carry `sub` (username),
`role`, `type` (`access`/`refresh`), `iat`, and `exp`.

`STARCORE_INITIAL_ADMIN_PASSWORD` bootstraps a first `admin` user at startup;
the call is idempotent (skips if the `admin` user already exists).

## Alternatives considered

1. **OAuth2 / OpenID Connect:** rejected as disproportionate — a homelab
   deployment does not need a full identity provider.
2. **Per-user API keys instead of JWTs:** considered, but JWTs are
   self-contained (no DB lookup on every request) and carry the role directly,
   which simplifies the auth hot-path.
3. **Global `STARCORE_TASK_TIMEOUT_SECONDS` applied to all token operations:**
   not applicable here; BCrypt hashing is CPU-bound and fast enough at
   gensalt default rounds (12) without a timeout.

## Consequences

- Existing `X-API-Key`-based integrations (CI scripts, monitoring, all tests
  written before REC-001) continue to work without any change — they receive
  `admin` role silently.
- Adding `STARCORE_JWT_SECRET_KEY` opts into the new model; omitting it keeps
  the old model. Both can coexist in the same deployment indefinitely.
- Audit trail: JWT-authenticated requests carry a `sub` (username) in the
  token, which is available in the `UserPrincipal` returned by
  `get_current_user()`. Future logging middleware could record it.
- Key rotation: JWT secret rotation invalidates all outstanding tokens. A
  dual-secret grace-period mechanism was not added (not needed at current scale).
- Regression coverage: `tests/test_jwt_auth.py` covers 46 scenarios including
  all token lifecycle paths, every role boundary, legacy coexistence, initial
  admin bootstrap, and the startup event handler.
