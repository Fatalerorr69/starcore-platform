# TECHNOLOGY PROFILE — FastAPI

```yaml
name: FastAPI
purpose: HTTP API framework — hlavní vstupní bod STARCORE Platform (MOD-001)
category: Development / Web Framework
version: ">=0.116.0"
official_source: SRC-FASTAPI-001
```

## DEPENDENCIES
uvicorn (ASGI server), Pydantic v2 (validace), Starlette (podkladová vrstva).

## COMPATIBILITY
Plně kompatibilní s Python 3.12+, Pydantic v2, async/await.

## INSTALLATION
Součást `platform/pyproject.toml` dependencies, instalováno přes `uv sync`.

## CONFIGURATION
`platform/packages/core/main.py` — app definice, middleware (slowapi rate limiting), routers registrace.

## SECURITY
- X-API-Key autentizace na všech endpointech kromě `/` a `/health` (ADR-012)
- Rate limiting přes slowapi (ADR-003)
- Request correlation (X-Request-ID, ADR-015)

## AUTOMATION
Auto-generovaná OpenAPI/Swagger dokumentace na `/docs`.

## INTEGRATION
Routery: `ai`, `auth`, `blueprints`, `diagnostics`, `providers`, `runs`, `ws` (`platform/packages/core/routers/`).
⚠️ Chybí API verzování (`/api/v1/`) — viz SES-001 §6 gap.

## STARCORE_USAGE
Kompletní HTTP API vrstva platformy — providers management, blueprint plan/run, AI blueprint generation, diagnostics, metrics.

## RISKS
Bez API verzování hrozí breaking changes pro klienty při budoucích úpravách endpointů (zaznamenáno v SES-001 jako MAJOR change čekající na schválení).

## UPDATE_POLICY
Sledovat FastAPI/Pydantic major verze; review při upgrade přes `uv lock`.
```
