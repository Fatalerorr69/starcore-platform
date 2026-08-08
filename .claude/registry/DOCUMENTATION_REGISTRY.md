# DOCUMENTATION REGISTRY

Aktualizováno: 2026-08-08 | Standard: SPOS-006

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
| SPOS-007 | Infrastructure Control Engine | `.claude/context/INFRASTRUCTURE_MAP.md` + HARDWARE/COMPUTE/CONTAINER/REMOTE_SERVICE_REGISTRY | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-008 | Deployment Automation Engine | `.claude/context/DEPLOYMENT_ARCHITECTURE.md` + `DEPLOYMENT_REGISTRY.md` + `INSTALLER_STUDIO_PLAN.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-009 | Security & Compliance Engine | `.claude/registry/SECURITY_REGISTRY.md` + `SECURITY_BASELINE.md` + `VULNERABILITY_REGISTRY.md` | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-010/011 | AI Orchestration Engine | `.claude/registry/AGENT_REGISTRY.md` + `WORKFLOW_REGISTRY.md` + `.claude/context/AI_ORCHESTRATION_MODEL.md` + 7 dalších | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-012 | Integration Engine | `.claude/registry/COMPONENT_REGISTRY.md` + `API_REGISTRY.md` + `.claude/context/INTERFACE_REGISTRY.md` + 6 dalších | ✅ AKTIVNÍ | 1.0.0 |
| SPOS-013 | Automation Engine | `.claude/registry/AUTOMATION_REGISTRY.md` + `.claude/context/AUTOMATION_ENGINE.md` + `TRIGGER_REGISTRY.md` + `WORKFLOW_AUTOMATION.md` + `AUTOMATION_PIPELINES.md` + 4 dalších | ✅ AKTIVNÍ | 1.0.0 |

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
| DR-019 | SPOS-007 Implementation Report | `.claude/reports/SPOS-007-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-020 | SPOS-008 Implementation Report | `.claude/reports/SPOS-008-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-021 | SPOS-009 Implementation Report | `.claude/reports/SPOS-009-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-022 | SPOS-011 Implementation Report | `.claude/reports/SPOS-011-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-023 | AI Health Report | `.claude/reports/AI_HEALTH_REPORT.md` | ✅ HOTOVO |
| DR-024 | SPOS-012 Implementation Report | `.claude/reports/SPOS-012-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-025 | Component Registry | `.claude/registry/COMPONENT_REGISTRY.md` | ✅ HOTOVO |
| DR-026 | API Registry | `.claude/registry/API_REGISTRY.md` | ✅ HOTOVO |
| DR-027 | Interface Registry | `.claude/context/INTERFACE_REGISTRY.md` | ✅ HOTOVO |
| DR-028 | Dependency Graph | `.claude/context/DEPENDENCY_GRAPH.md` | ✅ HOTOVO |
| DR-029 | Event Bus | `.claude/context/EVENT_BUS.md` | ✅ HOTOVO |
| DR-030 | Data Flow | `.claude/context/DATA_FLOW.md` | ✅ HOTOVO |
| DR-031 | Integration Map | `.claude/context/INTEGRATION_MAP.md` | ✅ HOTOVO |
| DR-032 | Integration Health | `.claude/context/INTEGRATION_HEALTH.md` | ✅ HOTOVO |
| DR-033 | Integration Recommendations | `.claude/context/INTEGRATION_RECOMMENDATIONS.md` | ✅ HOTOVO |
| DR-034 | SPOS-013 Implementation Report | `.claude/reports/SPOS-013-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-035 | Automation Registry | `.claude/registry/AUTOMATION_REGISTRY.md` | ✅ HOTOVO |
| DR-036 | Automation Engine | `.claude/context/AUTOMATION_ENGINE.md` | ✅ HOTOVO |
| DR-037 | Trigger Registry | `.claude/context/TRIGGER_REGISTRY.md` | ✅ HOTOVO |
| DR-038 | Workflow Automation | `.claude/context/WORKFLOW_AUTOMATION.md` | ✅ HOTOVO |
| DR-039 | Automation Pipelines | `.claude/context/AUTOMATION_PIPELINES.md` | ✅ HOTOVO |
| DR-040 | Self Maintenance Engine | `.claude/context/SELF_MAINTENANCE.md` | ✅ HOTOVO |
| DR-041 | Automation Health | `.claude/context/AUTOMATION_HEALTH.md` | ✅ HOTOVO |
| DR-042 | Automation Gap Analysis | `.claude/context/AUTOMATION_GAP_ANALYSIS.md` | ✅ HOTOVO |
| DR-043 | Automation Recommendations | `.claude/context/AUTOMATION_RECOMMENDATIONS.md` | ✅ HOTOVO |
| DR-044 | AAOS Architecture | `.claude/context/AAOS_ARCHITECTURE.md` | ✅ HOTOVO |
| DR-045 | Agent Lifecycle | `.claude/context/AGENT_LIFECYCLE.md` | ✅ HOTOVO |
| DR-046 | Multi-Agent Model | `.claude/context/MULTI_AGENT_MODEL.md` | ✅ HOTOVO |
| DR-047 | Provider Router V2 | `.claude/context/PROVIDER_ROUTER_V2.md` | ✅ HOTOVO |
| DR-048 | Context Engine | `.claude/context/CONTEXT_ENGINE.md` | ✅ HOTOVO |
| DR-049 | Prompt Engine | `.claude/context/PROMPT_ENGINE.md` | ✅ HOTOVO |
| DR-050 | AAOS Health | `.claude/context/AAOS_HEALTH.md` | ✅ HOTOVO |
| DR-051 | AAOS Gap Analysis | `.claude/context/AAOS_GAP_ANALYSIS.md` | ✅ HOTOVO |
| DR-052 | AAOS Recommendations | `.claude/context/AAOS_RECOMMENDATIONS.md` | ✅ HOTOVO |
| DR-053 | SPOS-014 Implementation Report | `.claude/reports/SPOS-014-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-054 | SPOS-015 Discovery Report | `.claude/reports/SPOS-015-DISCOVERY-REPORT.md` | ✅ HOTOVO |
| DR-055 | Ecosystem Map | `.claude/context/ECOSYSTEM_MAP.md` | ✅ HOTOVO |
| DR-056 | Legacy Registry | `.claude/registry/LEGACY_REGISTRY.md` | ✅ HOTOVO |
| DR-057 | Duplicate Registry | `.claude/registry/DUPLICATE_REGISTRY.md` | ✅ HOTOVO |
| DR-058 | Ecosystem Health | `.claude/context/ECOSYSTEM_HEALTH.md` | ✅ HOTOVO |
| DR-059 | Ecosystem Gap Analysis | `.claude/context/ECOSYSTEM_GAP_ANALYSIS.md` | ✅ HOTOVO |
| DR-060 | Ecosystem Recommendations | `.claude/context/ECOSYSTEM_RECOMMENDATIONS.md` | ✅ HOTOVO |
| DR-061 | SPOS-015 Implementation Report | `.claude/reports/SPOS-015-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |
| DR-062 | Repository Consolidation | `.claude/context/REPOSITORY_CONSOLIDATION.md` | ✅ HOTOVO |
| DR-063 | Legacy Migration Plan | `.claude/context/LEGACY_MIGRATION_PLAN.md` | ✅ HOTOVO |
| DR-064 | Module Classification | `.claude/context/MODULE_CLASSIFICATION.md` | ✅ HOTOVO |
| DR-065 | Dependency Analysis | `.claude/context/DEPENDENCY_ANALYSIS.md` | ✅ HOTOVO |
| DR-066 | Code Duplication Report | `.claude/context/CODE_DUPLICATION_REPORT.md` | ✅ HOTOVO |
| DR-067 | Architecture Alignment | `.claude/context/ARCHITECTURE_ALIGNMENT.md` | ✅ HOTOVO |
| DR-068 | Root Directory Audit | `.claude/context/ROOT_DIRECTORY_AUDIT.md` | ✅ HOTOVO |
| DR-069 | Technical Debt Register | `.claude/context/TECHNICAL_DEBT_REGISTER.md` | ✅ HOTOVO |
| DR-070 | Consolidation Roadmap | `.claude/context/CONSOLIDATION_ROADMAP.md` | ✅ HOTOVO |
| DR-071 | SPOS-016 Implementation Report | `.claude/reports/SPOS-016-IMPLEMENTATION-REPORT.md` | ✅ HOTOVO |

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
| `ECOSYSTEM_MAP.md` | STŘEDNÍ | ✅ HOTOVO (DR-055) |
| 16 zbývajících Technology Profiles | STŘEDNÍ | ⏳ PLÁNOVÁNO |
| SPOS-007+ | VYSOKÁ | ⏳ ČEKÁ |
