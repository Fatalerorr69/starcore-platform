# DEPLOYMENT ARCHITECTURE

Standard: SPOS-008 §3, §18 | Aktualizováno: 2026-08-06

---

## KLÍČOVÝ NÁLEZ (PHASE 1-2)

Repozitář obsahuje **dvě zcela oddělené deployment cesty**, které se snadno pletou kvůli podobným názvům:

### TRACK A — STARCORE Platform (Docker/CI, REÁLNÝ produkční deployment)

```
GitHub push/tag
  │
  ▼
platform/.github/workflows/ci.yml (lint/test/security/build)
  │
  ▼
platform/Dockerfile (multi-stage, python:3.12-slim, uv sync --frozen --no-dev)
  │
  ▼
platform/docker-compose.yml (api service + scaffold: postgres/redis/nats)
  │
  ▼
Funkční STARCORE Platform API
```

Ověřeno živě (SPOS-005/007): Dockerfile validní, `docker-compose.yml` definuje reálné služby, CI toolchain (pytest/ruff/pyright/bandit/pip-audit) čistý.

### TRACK B — install_*.sh (Termux/Android Edge, HISTORICKÉ STUB SKRIPTY)

```
$ head -1 install_*.sh
#!/data/data/com.termux/files/usr/bin/bash
```

**Živě ověřeno: všech 65/65 `install_*.sh` skriptů má tento shebang** — cílí výhradně na Termux (Android), ne na obecný Linux/Proxmox server. Obsah (viz `install_8A_ai_core_foundation_MASTER.sh`) generuje adresářovou strukturu a **stub Python soubory** (`{"component": "...", "status": "online"}`) — stejný vzorec, jaký SAKB-000 odhalil u `knowledge/core/knowledge_core.py`. Toto **není** funkční deployment automation, je to scaffolding generátor z předchozích sessions.

**Důsledek:** SPOS-008 §2 ("nevytvářej nový deployment framework, adoptuj existující") se vztahuje na **Track A** (Docker/CI). Track B nelze "adoptovat" jako produkční deployment mechanismus — je zaznamenán jako historický artefakt.

---

## ROOT-LEVEL GITHUB WORKFLOWS (další nález)

Root `.github/workflows/` obsahuje kromě `ci.yml` (reálný, spouští testy v `platform/`) i tři lehké/scaffoldingové workflow soubory:

| Workflow | Obsah | Hodnocení |
|---|---|---|
| `starcore-release.yml` | Jen `git status/branch/log`, `du -sh .` | Placeholder, nedělá reálný release |
| `starcore-integrity.yml` | `python -m compileall core platform` (adresář `core` na rootu NEEXISTUJE), `find security` | Částečně rozbitý (odkazuje na neexistující cestu) |
| `starcore-security.yml` | gitleaks scan (schedule) + `find *.pyc` | Jediný z trojice, který dělá něco reálného (gitleaks) |

---

## DEPLOYMENT MODEL (§3, aplikováno na Track A)

```
DISCOVERY   → tento SPOS-008 audit
PLAN        → DEPLOYMENT_REGISTRY.md + INSTALLER_STUDIO_PLAN.md
PROVISION   → Proxmox VM (SPOS-007, nedostupné z tohoto prostředí)
CONFIGURE   → .env + docker-compose.yml (existuje)
INSTALL     → docker compose up (netestováno zde — Docker daemon neběží)
VALIDATE    → CI toolchain (SPOS-005, živě ověřeno: PASS)
REGISTER    → DEPLOYMENT_REGISTRY.md
DOCUMENT    → tento dokument + platform/docs/installation.md (existuje)
```

---

## ENVIRONMENT PROFILES (§4)

| Profile | Target | Status |
|---|---|---|
| DEV | Lokální (uv run, SQLite) | ✅ AKTIVNÍ, ověřeno SPOS-005 |
| TEST | CI (GitHub Actions, ephemeral) | ✅ AKTIVNÍ (ci.yml) |
| STAGING | Nedefinováno | ❌ NEEXISTUJE |
| PRODUCTION | Proxmox VM + Docker (plánováno) | ⏳ PLÁNOVÁNO (VM-101, SPOS-007) |
| EDGE | Android/Termux | ⚠️ POUZE STUB SKRIPTY, ne funkční deployment |

---

## SECRETS MANAGEMENT (§13 — ověřeno)

`.env` je gitignored, `STARCORE_API_KEY`/`STARCORE_ANTHROPIC_API_KEY`/`STARCORE_PROXMOX_TOKEN_VALUE` čteny z env vars (`pydantic-settings`). Žádné secrets nalezeny v `.claude/`, `knowledge/`, ani v tomto auditu (dodrženo SES-000 P007, ověřeno gitleaks v `starcore-security.yml`).
