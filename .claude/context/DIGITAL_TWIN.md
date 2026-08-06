# STARCORE DIGITAL TWIN

Aktualizováno: 2026-08-06 | Standard: SES-000 P6

Tento soubor je digitální obraz aktuálního stavu systému STARCORE.
Musí být aktualizován po každé významné změně.

---

## REPOSITORY STATE

```yaml
repository: Fatalerorr69/starcore-platform
branch_main: main
branch_active: claude/starcore-ai-bootstrap-fkyb96
last_commit: 4fd5696 (Bootstrap 00 initialization)
status: clean
platform_version: 0.6.0
```

---

## ARCHITEKTURA

```yaml
platform:
  type: modular_monolith
  language: Python 3.12+
  framework: FastAPI + Typer
  database: SQLite (dev) / PostgreSQL (prod, plánováno)
  providers:
    - Docker (aktivní)
    - Proxmox VE (aktivní)
  ai_providers:
    - Anthropic Claude (volitelný)
    - OpenAI-compatible (Ollama, vLLM)
  tests: 601 passing
  coverage: 100% floor
  adr_count: 17
```

---

## INFRASTRUKTURA

```yaml
current_environment:
  type: cloud_container
  os: Linux 6.18.5-fc-v18
  cpu: Intel Xeon 2.80GHz
  ram: 15GiB
  disk_total: 252GB
  disk_used: 7.1GB
  docker: "29.3.1"
  python: "3.11.15"
  nodejs: "22.22.2"

target_infrastructure:
  hypervisor: Proxmox VE
  status: planned
  vms:
    - name: ai-core
      ram: 8GB
      cpu: 4
      disk: 100GB
      services: [ollama, open-webui, qdrant, redis, starcore-api]
    - name: database
      ram: 4GB
      services: [postgresql]
    - name: monitoring
      ram: 2GB
      services: [prometheus, grafana]
```

---

## MODULY

```yaml
active_modules:
  - id: MOD-001..009
    location: platform/
    status: production
    tested: true

  - id: MOD-010..015
    location: agents/, knowledge/, security/, intelligence/, control_center/, ai_core/
    status: active
    tested: false
    documented: false

planned_modules:
  - Docker AI Stack (MOD-100)
  - Ansible Playbooks (MOD-103)
  - Proxmox VM Blueprints (MOD-104)
```

---

## SES STAV

```yaml
ses_documents:
  SES-000: ACTIVE
  SES-001: PENDING
  SAKB-000: PENDING
  SPOS-000: PENDING
```

---

## BEZPEČNOST

```yaml
security:
  api_auth: X-API-Key header
  sast: Bandit (každý PR)
  secret_scan: gitleaks (každý PR + nightly)
  dependency_audit: pip-audit
  rbac: none (ADR-012, single key)
  plugin_sandbox: none (ADR-011, dokumentováno)
  tls: doporučeno v produkci
```

---

## DOKUMENTACE

```yaml
documentation_coverage:
  platform_readme: excellent
  architecture: excellent
  adr: excellent (17 docs)
  api: good
  cli: good
  security: good
  
  gaps:
    - INSTALL_SCRIPTS_REGISTRY (missing)
    - Docker AI Stack guide (missing)
    - Ansible guide (missing)
    - Integration map platform ↔ other layers (missing)
```

---

## POSLEDNÍ AKTUALIZACE HISTORY

| Datum | Změna | Autor |
|---|---|---|
| 2026-08-06 | Bootstrap 00 — Discovery reports, .claude/ struktura, root README | Claude Code |
| 2026-08-06 | SES-000 — Engineering Constitution registrace, všechny registry | Claude Code |
