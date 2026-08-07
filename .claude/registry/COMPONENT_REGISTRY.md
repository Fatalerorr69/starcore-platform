# COMPONENT REGISTRY

Standard: SPOS-012 §2-3 | Aktualizováno: 2026-08-07

Kompletní registr všech komponent STARCORE ekosystému. Klasifikace vychází z živého auditu.

Typy: CORE | SERVICE | MODULE | PLUGIN | PROVIDER | EDGE | TOOL | SCRIPT | DOCUMENTATION | LEGACY | STUB | TEST | GOVERNANCE

---

## CORE PLATFORM (platform/ — plně otestováno, 796 testů)

| ID | Name | Type | Location | Status | Version | Purpose |
|---|---|---|---|---|---|---|
| COMP-001 | Platform API | CORE | `platform/packages/core/` | AKTIVNÍ | 0.6.0 | FastAPI HTTP entry point, auth, metrics, events |
| COMP-002 | Blueprint Engine | CORE | `platform/packages/blueprints/` | AKTIVNÍ | 0.6.0 | YAML → TaskGraph, Pydantic validation |
| COMP-003 | Orchestrator | CORE | `platform/packages/orchestrator/` | AKTIVNÍ | 0.6.0 | Async TaskGraph execution (Scheduler) |
| COMP-004 | Provider SDK | CORE | `platform/packages/provider_sdk/` | AKTIVNÍ | 0.6.0 | BaseProvider ABC, ProviderRegistry |
| COMP-005 | Docker Provider | PROVIDER | `platform/packages/providers/docker/` | KÓDOVĚ OK / OFFLINE | 0.6.0 | Docker container lifecycle |
| COMP-006 | Proxmox Provider | PROVIDER | `platform/packages/providers/proxmox/` | KÓDOVĚ OK / OFFLINE | 0.6.0 | Proxmox VE VM/LXC management |
| COMP-007 | Kubernetes Provider | PROVIDER | `platform/packages/providers/kubernetes/` | KÓDOVĚ OK / OFFLINE | 0.6.0 | Kubernetes resource management |
| COMP-008 | AI Provider | MODULE | `platform/packages/ai/` | AKTIVNÍ | 0.6.0 | AIProvider ABC, Anthropic + OpenAI-compat |
| COMP-009 | CLI | TOOL | `platform/apps/cli/` | AKTIVNÍ | 0.6.0 | Typer CLI (blueprint/health/doctor/audit/...) |
| COMP-010 | Plugin System | MODULE | `platform/plugins/` | AKTIVNÍ | 0.6.0 | register(context) plugin interface |

---

## PLATFORM PLUGINS

| ID | Name | Type | Location | Status | Purpose |
|---|---|---|---|---|---|
| COMP-011 | Example Provider Plugin | PLUGIN | `platform/plugins/example_provider/` | AKTIVNÍ (demo) | Demo plugin pro provider registraci |
| COMP-012 | Run Logger Plugin | PLUGIN | `platform/plugins/run_logger/` | AKTIVNÍ | Logování blueprint runů do souboru |

---

## PLATFORM TOOLCHAIN

| ID | Name | Type | Location | Status | Purpose |
|---|---|---|---|---|---|
| COMP-013 | QC Engine | SCRIPT | `platform/.starcore/scripts/qc_engine.py` | AKTIVNÍ | CI gate orchestration (7 nástrojů) |
| COMP-014 | Impact Analyzer | SCRIPT | `platform/.starcore/scripts/impact_analyzer.py` | AKTIVNÍ | Change → test mapping |
| COMP-015 | Release Readiness | SCRIPT | `platform/.starcore/scripts/release_readiness.py` | AKTIVNÍ | 12-gate release validation |
| COMP-016 | Decision Engine | SCRIPT | `platform/.starcore/scripts/decision_engine.py` | AKTIVNÍ | Governance reporting formát |
| COMP-017 | Session Ledger | SCRIPT | `platform/.starcore/scripts/ledger.py` | AKTIVNÍ | Session lifecycle management |
| COMP-018 | Prompt Registry | SCRIPT | `platform/.starcore/scripts/registry.py` | AKTIVNÍ | Prompt CRUD + validation |
| COMP-019 | Startup Protocol | SCRIPT | `platform/.starcore/scripts/startup_protocol.py` | AKTIVNÍ | Rychlá kontrola prostředí |
| COMP-020 | Health Script | SCRIPT | `platform/scripts/health.py` | AKTIVNÍ | Platform health check |
| COMP-021 | Doctor Script | SCRIPT | `platform/scripts/doctor.py` | AKTIVNÍ | Diagnostic tool |

---

## GOVERNANCE LAYER (.claude/)

| ID | Name | Type | Location | Status | Purpose |
|---|---|---|---|---|---|
| COMP-030 | SES Documents | DOCUMENTATION | `.claude/ses/` | AKTIVNÍ | Engineering Constitution + Technical Standard |
| COMP-031 | SAKB Knowledge Model | DOCUMENTATION | `.claude/sakb/` | AKTIVNÍ | Knowledge governance |
| COMP-032 | SPOS Runtime Bootstrap | DOCUMENTATION | `.claude/spos/` | AKTIVNÍ | Project OS bootstrap |
| COMP-033 | Registry System | DOCUMENTATION | `.claude/registry/` | AKTIVNÍ | 15+ registry souborů |
| COMP-034 | Digital Twin | DOCUMENTATION | `.claude/context/DIGITAL_TWIN.md` | AKTIVNÍ | Live system snapshot |
| COMP-035 | Context Protocol | DOCUMENTATION | `.claude/context/CONTEXT_RESTORATION_PROTOCOL.md` | AKTIVNÍ | AI cold-start protocol |

---

## KNOWLEDGE BASE

| ID | Name | Type | Location | Status | Purpose |
|---|---|---|---|---|---|
| COMP-040 | Technology Profiles | DOCUMENTATION | `knowledge/technologies/` | ČÁSTEČNÉ (6/22) | Strukturované tech znalosti |
| COMP-041 | Knowledge Packages | DOCUMENTATION | `knowledge/packages/` | ČÁSTEČNÉ (1) | Cross-tech patterns |
| COMP-042 | Source Registry | DOCUMENTATION | `knowledge/registry/` | AKTIVNÍ (9 zdrojů) | L5 knowledge sources |

---

## CI/CD (GitHub Actions)

| ID | Name | Type | Location | Status | Purpose |
|---|---|---|---|---|---|
| COMP-050 | CI Pipeline | SERVICE | `.github/workflows/ci.yml` | AKTIVNÍ | pytest + ruff + pyright + bandit + pip-audit |
| COMP-051 | Security Scan | SERVICE | `.github/workflows/starcore-security.yml` | AKTIVNÍ | gitleaks secret scan |
| COMP-052 | Integrity Check | SERVICE | `.github/workflows/starcore-integrity.yml` | ROZBITÉ | Odkazuje na neexistující root `core/` |
| COMP-053 | Release Pipeline | SERVICE | `.github/workflows/release.yml` | AKTIVNÍ | Release automation |
| COMP-054 | Platform CI | SERVICE | `platform/.github/workflows/ci.yml` | ORPHANED | GitHub nečte platform/.github/ |
| COMP-055 | Docker Publish | SERVICE | `platform/.github/workflows/docker-publish.yml` | ORPHANED | GitHub nečte platform/.github/ |

---

## SCAFFOLD SERVICES (docker-compose.yml — neaktivní)

| ID | Name | Type | Status | Purpose |
|---|---|---|---|---|
| COMP-060 | PostgreSQL | SERVICE | PLÁNOVANÝ (scaffold profile) | Produkční databáze |
| COMP-061 | Redis | SERVICE | PLÁNOVANÝ (scaffold profile) | Cache / queue |
| COMP-062 | NATS | SERVICE | PLÁNOVANÝ (scaffold profile) | Message bus |

---

## TERMUX / ANDROID STUBS (root-level, nepoužitelné mimo Termux)

| ID | Name | Type | Location | Status | Potvrzení |
|---|---|---|---|---|---|
| COMP-070 | Agents stubs | STUB | `agents/` | STUB | JSON print, prázdná logika |
| COMP-071 | AI Runtime stubs | STUB | `ai_runtime/` | STUB | ~/STARCORE path |
| COMP-072 | Autonomous stubs | STUB | `autonomous/` | STUB | ~/STARCORE path |
| COMP-073 | Distributed stubs | STUB | `distributed/` | STUB | ~/STARCORE path |
| COMP-074 | Mission Engine stubs | STUB | `mission_engine/` | STUB | ~/STARCORE path |
| COMP-075 | Knowledge Engine stub | STUB | `knowledge_engine/` | STUB | ~/STARCORE path |
| COMP-076 | AI Core stub | STUB | `ai_core/` | STUB | JSON print |
| COMP-077 | Security stubs | STUB | `security/` | STUB | ~/STARCORE path |
| COMP-078 | Intelligence stubs | STUB | `intelligence/` | STUB | ~/STARCORE path |
| COMP-079 | Control Center stubs | STUB | `control_center/` | STUB | ~/STARCORE path |
| COMP-080 | Runtime/Android dirs | STUB | `runtime/android/` | STUB | 100+ adresářů, ~/STARCORE |
| COMP-081 | GitHub Intelligence | STUB | `github_intelligence/` | STUB | ~/STARCORE path |
| COMP-082 | 65 install_*.sh scripts | STUB | root `install_*.sh` | STUB | #!/data/data/com.termux/... shebang |
| COMP-083 | Installers/Android | STUB | `installers/android/` | STUB | Termux/Android |

---

## STATISTIKY

```yaml
total_components: 51 (catalogued groups, actual files: 150+)
type_breakdown:
  CORE: 8 (COMP-001..008)
  PROVIDER: 3 (COMP-005..007)
  MODULE: 2 (COMP-008..009 overlap + plugin system)
  PLUGIN: 2 (COMP-011..012)
  SCRIPT/TOOL: 10 (COMP-009, 013..021)
  DOCUMENTATION/GOVERNANCE: 10 (COMP-030..042)
  SERVICE/CI: 6 (COMP-050..055)
  SCAFFOLD: 3 (COMP-060..062)
  STUB: 14 (COMP-070..083)
real_vs_stub_ratio: "~30 reálných / ~14+ stub skupin"
```
