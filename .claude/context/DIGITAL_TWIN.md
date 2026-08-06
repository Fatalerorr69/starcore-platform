# STARCORE DIGITAL TWIN

Aktualizováno: 2026-08-06 | Standard: SES-001 §17

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
  SES-001: ACTIVE
  SAKB-000: ACTIVE
  SPOS-000: ACTIVE

spos_status:
  discovery: "platform/.starcore/ already exists — mature runtime (3843 lines Python, 171 tests)"
  decision: "Adopted existing platform/.starcore/ as canonical SPOS implementation; no duplicate created at root"
  modules_fully_covered: [SPOS-001, SPOS-002, SPOS-003, SPOS-005]
  modules_partial: [SPOS-004, SPOS-008]
  modules_missing: [SPOS-006, SPOS-007, SPOS-009]
  duplicate_concept: "SPOS-010 — two digital twin docs with different scope (ecosystem vs platform); platform snapshot STALE (v0.4.0 vs actual v0.6.0)"
  correction_to_ses_001: "Dependabot + SBOM configs DO exist (platform/.github/) but are orphaned — GitHub only reads root .github/, not nested platform/.github/"

ses_001_compliance:
  platform_layer: COMPLIANT
  root_ecosystem_layer: PARTIAL — formal exception granted (SES-001 §2, Variant B)
    known_gaps:
      - API not versioned (/api/v1/ missing) — MAJOR change, awaiting approval
      - No dependabot.yml / SBOM
      - No documentation-check CI step
      - MOD-010..015 (agents, knowledge, security, intelligence, control_center, ai_core) undocumented, untested
  target_state: full migration to packages/apps/services layout (SES-001 §2 Variant A) — requires user approval before file moves
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

## KNOWLEDGE STATUS (SAKB-000 §18)

```yaml
knowledge_base:
  sources_registered: 9
  sources_planned: 12
  technology_profiles_created: 6
  technology_profiles_planned: 16
  knowledge_packages_created: 1
  research_pipeline: defined_not_automated
  rag_embedding_pipeline: not_implemented
  known_conflicts:
    - "Python 3.11 (environment) vs >=3.12 (platform pyproject.toml requirement) — mitigated via uv"
```

---

## POSLEDNÍ AKTUALIZACE HISTORY

| Datum | Změna | Autor |
|---|---|---|
| 2026-08-06 | Bootstrap 00 — Discovery reports, .claude/ struktura, root README | Claude Code |
| 2026-08-06 | SES-000 — Engineering Constitution registrace, všechny registry | Claude Code |
| 2026-08-06 | SES-001 — Technical Standard gap analýza, MODULE/AI registry rozšíření | Claude Code |
| 2026-08-06 | SAKB-000 — Knowledge Base struktura, 6 Technology Profiles, Source/Knowledge Registry | Claude Code |
| 2026-08-06 | SPOS-000 — Discovery existujícího platform/.starcore/ runtime, formální adopce, SPOS_REGISTRY, oprava SES-001 (Dependabot/SBOM orphaned) | Claude Code |
