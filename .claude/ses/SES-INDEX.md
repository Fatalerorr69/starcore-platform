# SES — STARCORE ENGINEERING STANDARD INDEX

Aktualizováno: 2026-08-06

---

## POŘADÍ IMPLEMENTACE

| Dokument | Název | Status | Soubor |
|---|---|---|---|
| SES-000 | Engineering Constitution | ✅ AKTIVNÍ | `SES-000-ENGINEERING-CONSTITUTION.md` |
| SES-001 | Technical Engineering Standard | ✅ AKTIVNÍ | `SES-001-TECHNICAL-STANDARD.md` |
| SAKB-000 | Knowledge Model | ✅ AKTIVNÍ | `../sakb/SAKB-000-KNOWLEDGE-MODEL.md` |
| SPOS-000 | Runtime Bootstrap | ✅ AKTIVNÍ | `../spos/SPOS-000-RUNTIME-BOOTSTRAP.md` |
| SPOS-001 | Project Memory Engine | ✅ AKTIVNÍ | (implementováno přímo v `platform/.starcore/`, viz SPOS_REGISTRY.md) |
| SPOS-002 | Session Management Engine | ✅ AKTIVNÍ | (implementováno přímo v `platform/.starcore/sessions/`, viz SPOS_REGISTRY.md) |
| SPOS-003 | Prompt Registry Engine | ✅ AKTIVNÍ | (implementováno přímo v `platform/.starcore/prompts/`, viz SPOS_REGISTRY.md) |
| SPOS-004 | Project Intelligence Engine | ✅ AKTIVNÍ | (existující QC engines formálně adoptovány, viz INTELLIGENCE_REGISTRY.md) |
| SPOS-005 | Audit Engine | ✅ AKTIVNÍ | (plný CI toolchain živě spuštěn, viz AUDIT_REGISTRY.md a FIRST_FULL_AUDIT_REPORT.md) |
| SPOS-006 | Documentation Engine | ✅ AKTIVNÍ | (mkdocs build --strict živě ověřen, viz DOCUMENTATION_MAP.md a DOCUMENTATION_HEALTH_REPORT.md) |
| SPOS-007 | Infrastructure Control Engine | ✅ AKTIVNÍ | (starcore diagnose živě ověřen, viz INFRASTRUCTURE_MAP.md a 4 nové registry) |
| SPOS-008 | Deployment Automation Engine | ✅ AKTIVNÍ | (65 install skriptů auditováno — Termux stub, ne produkce; viz DEPLOYMENT_ARCHITECTURE.md) |
| SPOS-009 | Security & Compliance Engine | ✅ AKTIVNÍ | (bandit/pip-audit/gitleaks CI živě ověřeno; viz SECURITY_REGISTRY.md, SECURITY_BASELINE.md, VULNERABILITY_REGISTRY.md) |
| SPOS-010/011 | AI Orchestration Engine (prompt označen SPOS-011, viz SPOS_REGISTRY poznámka) | ✅ AKTIVNÍ | (existující orchestrator/ai packages auditovány; viz AGENT_REGISTRY.md, AI_ORCHESTRATION_MODEL.md) |
| SPOS-012 | Integration Engine | ✅ AKTIVNÍ | (9 souborů: COMPONENT_REGISTRY, API_REGISTRY, INTERFACE_REGISTRY, DEPENDENCY_GRAPH, EVENT_BUS, DATA_FLOW, INTEGRATION_MAP, INTEGRATION_HEALTH, INTEGRATION_RECOMMENDATIONS) |
| SPOS-013+ | SPOS Modules | ⏳ ČEKÁ | TBD (další prompt: Automation Engine dle §18 SPOS-012) |

---

## VRSTVY ARCHITEKTURY

```
LAYER 1 — Engineering Standard (SES)
  └── SES-000 ✅
  └── SES-001 ✅

LAYER 2 — Knowledge System (SAKB)
  └── SAKB-000 ✅

LAYER 3 — Project OS (SPOS)
  └── SPOS-000 ✅ (existující platform/.starcore/ formálně adoptován)
  └── SPOS-001..010 — 4 plně pokryty, 2 částečně, 3 gaps (viz SPOS_REGISTRY.md)

LAYER 4 — Adapters
  └── Claude Code (aktivní)
  └── Codex, Gemini (budoucí)
```
