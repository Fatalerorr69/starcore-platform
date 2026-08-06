# DOCUMENTATION REGISTRY

Aktualizováno: 2026-08-06 | Standard: SPOS-006

Formát dle SPOS-006 §3: DOCUMENT_ID/TITLE/TYPE/VERSION/STATUS/OWNER/RELATED_COMPONENTS/RELATED_CODE/RELATED_REGISTRY/LAST_VALIDATION — plně aplikováno na governance dokumenty (SES/SAKB/SPOS níže); pro `platform/docs/` (56 souborů, existující, dobře udržované) viz zjednodušený přehled a `DOCUMENTATION_MAP.md` pro plnou mapu podle typu (§4).

---

## SES — ENGINEERING STANDARD

| ID | Název | Soubor | Status | Verze |
|---|---|---|---|---|
| SES-000 | Engineering Constitution | `.claude/ses/SES-000-ENGINEERING-CONSTITUTION.md` | ✅ AKTIVNÍ | 1.0.0 |
| SES-001 | Technical Engineering Standard | `.claude/ses/SES-001-TECHNICAL-STANDARD.md` | ✅ AKTIVNÍ | 1.0.0 |
| SAKB-000 | Knowledge Model | `.claude/sakb/SAKB-000-KNOWLEDGE-MODEL.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-000 | Runtime Bootstrap | `.claude/spos/SPOS-000-RUNTIME-BOOTSTRAP.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-001 | Project Memory Engine | implementováno v `platform/.starcore/` + `.claude/context/CONTEXT_RESTORATION_PROTOCOL.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-002 | Session Management Engine | implementováno v `platform/.starcore/sessions/` + `.claude/registry/SESSION_REGISTRY.md` + `.claude/context/SESSION_CONTEXT.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-003 | Prompt Registry Engine | implementováno v `platform/.starcore/prompts/` + `.claude/registry/PROMPT_REGISTRY.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-004 | Project Intelligence Engine | `.claude/registry/INTELLIGENCE_REGISTRY.md` + `.claude/reports/SPOS-004-HEALTH-REPORT.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-005 | Audit Engine | `.claude/registry/AUDIT_REGISTRY.md` + `.claude/reports/FIRST_FULL_AUDIT_REPORT.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-006 | Documentation Engine | `.claude/context/DOCUMENTATION_MAP.md` + `.claude/reports/DOCUMENTATION_HEALTH_REPORT.md` | ✅ AKTIVNÍ | 1.0.0 |

---

## DISCOVERY / IMPLEMENTATION REPORTS

| ID | Název | Soubor | Status |
|---|---|---|---|
| DR-001 | Initial Discovery Report | `.claude/reports/STARCORE_INITIAL_DISCOVERY_REPORT.md` | ✅ HOTOVO |
| DR-002 | Repository Analysis | `.claude/reports/REPOSITORY_ANALYSIS.md` | ✅ HOTOVO |
| DR-003 | Current Architecture | `.claude/reports/CURRENT_ARCHITECTURE.md` | ✅ HOTOVO |
| DR-004 | Documentation Audit | `.claude/reports/DOCUMENTATION_AUDIT.md` | ✅ HOTOVO |
| DR-005 | Improvement Roadmap | `.claude/reports/IMPROVEMENT_ROADMAP.md` | ✅ HOTOVO |
| DR-006 | Final Initialization Report (Bootstrap 00) | `.claude/reports/FINAL_INITIALIZATION_REPORT.md` | ✅ HOTOVO |
| DR-007 | SES-001 Implementation Report | `.claude/reports/SES-001-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-008 | SAKB-000 Implementation Report | `.claude/reports/SAKB-000-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-009 | SPOS-000 Implementation Report | `.claude/reports/SPOS-000-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-010 | SPOS-001 Implementation Report | `.claude/reports/SPOS-001-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-011 | SPOS-002 Implementation Report | `.claude/reports/SPOS-002-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-012 | SPOS-003 Implementation Report | `.claude/reports/SPOS-003-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-013 | SPOS-004 Health Report | `.claude/reports/SPOS-004-HEALTH-REPORT.md` | ✅ HOTOVO |
| DR-014 | SPOS-004 Implementation Report | `.claude/reports/SPOS-004-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-015 | First Full Audit Report | `.claude/reports/FIRST_FULL_AUDIT_REPORT.md` | ✅ HOTOVO |
| DR-016 | SPOS-005 Implementation Report | `.claude/reports/SPOS-005-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-017 | Documentation Health Report | `.claude/reports/DOCUMENTATION_HEALTH_REPORT.md` | ✅ HOTOVO |
| DR-018 | SPOS-006 Implementation Report | `.claude/reports/SPOS-006-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |

---

## SAKB — KNOWLEDGE BASE (`knowledge/`)

| Kategorie | Počet položek | Status |
|---|---|---|
| Technology Profiles | 6 vytvořeno / 22 plánováno | ⚠️ ČÁSTEČNĚ |
| Knowledge Packages | 1 | ✅ ZALOŽENO |
| Source Registry | 9 zdrojů (L5) | ✅ ZALOŽENO |

Detail: `.claude/registry/KNOWLEDGE_REGISTRY.md`

---

## PLATFORM DOKUMENTACE (`platform/docs/`)

| Dokument | Status | Kvalita |
|---|---|---|
| README.md | ✅ | Výborná |
| docs/architecture.md | ✅ | Výborná |
| docs/api.md | ✅ | Dobrá |
| docs/cli.md | ✅ | Dobrá |
| docs/installation.md | ✅ | Dobrá |
| docs/security.md | ✅ | Dobrá |
| docs/plugins.md | ✅ | Dobrá |
| docs/testing/ | ✅ | Dobrá |
| docs/adr/ (17 ADRs) | ✅ | Výborná |
| CHANGELOG.md | ✅ | Přítomná |
| SECURITY.md | ✅ | Dobrá |
| CONTRIBUTING.md | ✅ | Přítomná |
| INTEGRATION_GUIDE.md | ✅ | Dobrá |

---

## DOCUMENTATION MAP A HEALTH (SPOS-006)

Plná mapa dokumentace dle typu (Architecture/Development/Operations/Infrastructure/AI/Knowledge): `.claude/context/DOCUMENTATION_MAP.md` (126 dokumentů celkem).
Audit D001-D006: `.claude/reports/DOCUMENTATION_HEALTH_REPORT.md` (9 nálezů).

## CHYBĚJÍCÍ DOKUMENTACE (prioritní)

| Dokument | Priorita | Status |
|---|---|---|
| STARCORE Installation Manual (SPOS-006 §10) | VYSOKÁ | ❌ CHYBÍ |
| `INSTALL_SCRIPTS_REGISTRY.md` | KRITICKÁ | ❌ CHYBÍ |
| `docker/ai-stack/README.md` | VYSOKÁ | ❌ CHYBÍ |
| USER_GUIDE (SPOS-006 §13) | STŘEDNÍ | ❌ CHYBÍ |
| `ansible/README.md` | STŘEDNÍ | ❌ CHYBÍ |
| `ECOSYSTEM_MAP.md` | STŘEDNÍ | ❌ CHYBÍ |
| 16 zbývajících Technology Profiles | STŘEDNÍ | ⏳ PLÁNOVÁNO |
| SPOS-007+ | VYSOKÁ | ⏳ ČEKÁ |
