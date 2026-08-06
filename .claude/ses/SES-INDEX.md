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
| SPOS-007+ | SPOS Modules | ⏳ ČEKÁ | TBD |

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
