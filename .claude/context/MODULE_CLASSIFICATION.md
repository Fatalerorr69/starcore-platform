# MODULE CLASSIFICATION

Standard: SPOS-016 §2 | Aktualizováno: 2026-08-08

Klasifikace všech modulů (Python packages, shell scripts, konfigurace) v celém repozitáři.

---

## ACTIVE MODULES (platform/packages/)

| Modul | Typ | Souborů | Testů | Coverage | Status |
|---|---|---|---|---|---|
| `packages/core/` | FastAPI app | 20+ | 200+ | 100% | ACTIVE |
| `packages/blueprints/` | Blueprint engine | 5+ | 80+ | 100% | ACTIVE |
| `packages/orchestrator/` | Task scheduler | 5+ | 60+ | 100% | ACTIVE |
| `packages/provider_sdk/` | Provider ABC | 4 | 40+ | 100% | ACTIVE |
| `packages/providers/docker/` | Docker adapter | 2 | 30+ | 100% | ACTIVE |
| `packages/providers/proxmox/` | Proxmox adapter | 2 | 30+ | 100% | ACTIVE |
| `packages/providers/kubernetes/` | K8s adapter | 2 | 30+ | 100% | ACTIVE |
| `packages/ai/` | AI provider | 4 | 40+ | 100% | ACTIVE |
| `apps/cli/` | Typer CLI | 1 | 50+ | 100% | ACTIVE |
| `plugins/example_provider/` | Example plugin | 1 | 10+ | 100% | ACTIVE |
| `plugins/run_logger/` | Run logger plugin | 1 | 10+ | 100% | ACTIVE |

## ACTIVE SUPPORT (platform/)

| Modul | Typ | Status |
|---|---|---|
| `.starcore/scripts/` | QC engines (8 scripts, 171 tests) | ACTIVE |
| `scripts/doctor.py` | Standalone QC runner | ACTIVE |
| `scripts/health.py` | Health check script | ACTIVE |
| `scripts/release.py` | Release helper | ACTIVE |
| `migrations/` | Alembic DB migrations | ACTIVE |
| `docs/` | MkDocs documentation (56 files) | ACTIVE |

## GOVERNANCE MODULES (.claude/)

| Modul | Typ | Souborů | Status |
|---|---|---|---|
| `.claude/ses/` | Engineering Standards | 2 | ACTIVE |
| `.claude/sakb/` | Knowledge Model | 1 | ACTIVE |
| `.claude/spos/` | Project OS Bootstrap | 1 | ACTIVE |
| `.claude/context/` | Context documents | 30+ | ACTIVE |
| `.claude/registry/` | Governance registries | 15+ | ACTIVE |
| `.claude/reports/` | Implementation reports | 25+ | ACTIVE |

## KNOWLEDGE MODULES (knowledge/)

| Modul | Typ | Status |
|---|---|---|
| `knowledge/registry/` | Source registry (YAML) | ACTIVE |
| `knowledge/technologies/` | 6 technology profiles | ACTIVE |
| `knowledge/core/knowledge_core.py` | JSON print stub | TERMUX |
| `knowledge/rag/rag_engine.py` | JSON print stub | TERMUX |

## TERMUX MODULES (root-level, ~/STARCORE target)

| Modul | Souborů | Pattern | Status |
|---|---|---|---|
| `plugins/enabled/android/` | 187 .py | `Path.home()/"STARCORE"` → JSON write | TERMUX |
| `agents/` | 3 .py | JSON print stubs | TERMUX |
| `ai_core/` | 1 .py | JSON print stub | TERMUX |
| `ai_runtime/` | 3 .py | JSON print stubs | TERMUX |
| `autonomous/` | 9 .py | `Path.home()/"STARCORE"` | TERMUX |
| `distributed/` | 9 .py | `Path.home()/"STARCORE"` | TERMUX |
| `tools/` | 18 .sh | Termux shell stubs | TERMUX |
| `install_*.sh` | 65 .sh | `#!/data/data/com.termux/...` | TERMUX |
| Root `starcore` | 1 .py | Termux entry point | TERMUX |

## LEGACY MODULES (root-level, nepoužívané)

| Modul | Souborů | Nahrazeno | Status |
|---|---|---|---|
| `core/` | 43 .py | `platform/packages/core/` | LEGACY |
| `control_center/` | 21 | `platform/apps/cli/` + API | LEGACY |
| `mission_engine/` | 3 .py | `platform/packages/orchestrator/` | LEGACY |
| `studio/` | 3 | `platform/ /ui endpoint` | LEGACY |
| `sdk/` | 4 .py | `platform/packages/provider_sdk/` | LEGACY |
| `hardening/` | 2 .py | CI gates (pip-audit, bandit) | LEGACY |
| `cli/` | 1 dir | `platform/apps/cli/` | LEGACY |
| `config/` | 5 JSON/YAML | pydantic-settings (env vars) | LEGACY |
| `security/` | 3 .py | CI gates + `core/security.py` | LEGACY |
| `automation/` | 21 .sh | `.starcore/scripts/` QC engines | LEGACY |
| `prompts/` | 4 .md | `.starcore/prompts/registry.yaml` | LEGACY |
| `sessions/` | 1 JSON | `.starcore/sessions/ledger.yaml` | LEGACY |
| `bin/` | 3 exec | `uv run starcore` | BROKEN |
| `backups/` | 1 .tar.gz | Git tags + releases | LEGACY |
| `installers/` | 10 | Docker/CI deployment | LEGACY |
| `templates/` | 1 JSON | Not needed | LEGACY |
| `bundles_7x/` | 5 .sh | Not needed | LEGACY |

## GENERATED DATA (runtime state, not code)

| Adresář | Souborů | Typ | Status |
|---|---|---|---|
| `runtime/` | 411 (405 JSON) | Termux-generated state | GENERATED |
| `intelligence/` | 9 (scan outputs) | Termux-generated reports | GENERATED |

## DEAD CODE (zero references)

| Modul | Soubor | Importován | Status |
|---|---|---|---|
| `github_intelligence/` | `github_scanner.py` | Nikde | DEAD → REMOVE |
| `knowledge_engine/` | `knowledge_core.py` | Nikde | DEAD → REMOVE |
| `performance/` | `performance_analyzer.py` | Nikde | DEAD → REMOVE |
| `api_gateway/` | `api_gateway.py` | Nikde | DEAD → REMOVE |

## DEPRECATED

| Položka | Důvod | Status |
|---|---|---|
| `registry/modules.json` | Prázdný JSON `{"modules": []}` | REMOVE |
| `registry/sdk_registry.json` | Prázdný | REMOVE |
| `runtime/marketplace/registry.json` | Prázdný JSON `{"plugins": []}` | REMOVE |
| `requirements.txt` (root) | Jen packaging/setuptools/wheel, nepoužívá se | REMOVE |
| `.envrc` | Odkazuje `.venv/` v root, stale | REMOVE |

---

## STATISTIKY

```yaml
total_modules: 85+

active: 17 (platform packages + apps + plugins + docs + scripts + QC)
governance: 6 (.claude/ subsystems)
knowledge: 4 (2 active, 2 termux stubs)
termux: 9 directories + 65 install scripts
legacy: 17 directories
generated: 2 directories (420 files)
dead: 4 directories
deprecated: 5 files

platform_test_coverage: 100%
platform_tests: 796
governance_documents: 107
```
