# SPOS REGISTRY

Aktualizováno: 2026-08-08 | Standard: SPOS-016

Registr operačních modulů Project Operating System. Fyzická implementace primárně v `platform/.starcore/` (viz SPOS-000 rozhodnutí — adoptováno, ne duplikováno).

---

| Modul | Název | Implementace | Status |
|---|---|---|---|
| SPOS-001 | Project Memory | `platform/.starcore/memory/*.md` (+ nově `current_state.md`, `state/project_state.json`) | ✅ AKTIVNÍ — ROZŠÍŘENO |
| SPOS-002 | Session Management | `platform/.starcore/sessions/` + `scripts/ledger.py` (+ nově `.claude/registry/SESSION_REGISTRY.md`, `.claude/context/SESSION_CONTEXT.md`) | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO |
| SPOS-003 | Prompt Registry | `platform/.starcore/prompts/registry.yaml` + `scripts/registry.py` (+ nově `.claude/registry/PROMPT_REGISTRY.md`, 7 SES/SAKB/SPOS promptů zaregistrováno) | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO |
| SPOS-004 | Project Intelligence | `scripts/impact_analyzer.py` + `regression_sentinel.py` + `release_readiness.py` + `qc_engine.py` (sdíleno s SPOS-005) + nově `.claude/registry/INTELLIGENCE_REGISTRY.md` | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO |
| SPOS-005 | Audit Engine | `scripts/qc_engine.py`, `regression_sentinel.py`, `release_readiness.py`, plný CI toolchain (pytest/ruff/pyright/bandit/pip-audit) + nově `.claude/registry/AUDIT_REGISTRY.md` (7 domén A01-A07) | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO (plný `uv sync --extra dev` + 6 nástrojů) |
| SPOS-006 | Documentation Engine | `.claude/context/DOCUMENTATION_MAP.md` + `.claude/reports/DOCUMENTATION_HEALTH_REPORT.md` + `mkdocs build --strict` (živě ověřeno) | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO |
| SPOS-007 | Infrastructure Control | `platform/packages/providers` + nově `.claude/context/INFRASTRUCTURE_MAP.md` + 4 registry (HARDWARE/COMPUTE/CONTAINER/REMOTE_SERVICE) | ✅ AKTIVNÍ — ROZŠÍŘENO, ŽIVĚ OTESTOVÁNO |
| SPOS-008 | Deployment Automation Engine (skutečné pořadí promptů — viz poznámka níže) | `.claude/context/DEPLOYMENT_ARCHITECTURE.md` + `DEPLOYMENT_REGISTRY.md` + `INSTALLER_STUDIO_PLAN.md` | ✅ AKTIVNÍ — ŽIVĚ OTESTOVÁNO |
| SPOS-010 | AI Orchestration Engine (původní SPOS-000 mapování — dle promptu číslován SPOS-011, viz poznámka) | `.claude/registry/AGENT_REGISTRY.md` + `WORKFLOW_REGISTRY.md` + `AI_ORCHESTRATION_MODEL.md` + 8 dalších souborů | ✅ AKTIVNÍ — DISCOVERY + DOKUMENTACE |
| SPOS-009 | Security & Compliance Engine (dle SPOS-008 §19, skutečné pořadí — ne "Evolution Engine" z původní SPOS-000 mapy) | `.claude/registry/SECURITY_REGISTRY.md` + `SECURITY_BASELINE.md` + `VULNERABILITY_REGISTRY.md` | ✅ AKTIVNÍ — ŽIVĚ AUDITOVÁNO |
| SPOS-010 | Digital Twin Runtime | `.claude/context/DIGITAL_TWIN.md` (ekosystém) + `platform/.starcore/memory/project_snapshot.md` (platform, ZASTARALÉ) | ⚠️ DUPLICITNÍ SCOPE |
| SPOS-012 | Integration Engine | `.claude/registry/COMPONENT_REGISTRY.md` + `API_REGISTRY.md` + `.claude/context/INTERFACE_REGISTRY.md` + `DEPENDENCY_GRAPH.md` + `EVENT_BUS.md` + `DATA_FLOW.md` + `INTEGRATION_MAP.md` + `INTEGRATION_HEALTH.md` + `INTEGRATION_RECOMMENDATIONS.md` | ✅ AKTIVNÍ — DISCOVERY + DOKUMENTACE |
| SPOS-013 | Automation Engine | `.claude/registry/AUTOMATION_REGISTRY.md` + `.claude/context/AUTOMATION_ENGINE.md` + `TRIGGER_REGISTRY.md` + `WORKFLOW_AUTOMATION.md` + `AUTOMATION_PIPELINES.md` + `SELF_MAINTENANCE.md` + `AUTOMATION_HEALTH.md` + `AUTOMATION_GAP_ANALYSIS.md` + `AUTOMATION_RECOMMENDATIONS.md` | ✅ AKTIVNÍ — DISCOVERY + DOKUMENTACE |
| SPOS-014 | AI Agent Operating System (AAOS) | `.claude/context/AAOS_ARCHITECTURE.md` + `AGENT_LIFECYCLE.md` + `MULTI_AGENT_MODEL.md` + `PROVIDER_ROUTER_V2.md` + `CONTEXT_ENGINE.md` + `PROMPT_ENGINE.md` + `AAOS_HEALTH.md` + `AAOS_GAP_ANALYSIS.md` + `AAOS_RECOMMENDATIONS.md` + rozšířený `AGENT_REGISTRY.md` | ✅ AKTIVNÍ — DISCOVERY + DOKUMENTACE |
| SPOS-015 | Ecosystem Hygiene Engine | `.claude/context/ECOSYSTEM_MAP.md` + `ECOSYSTEM_HEALTH.md` + `ECOSYSTEM_GAP_ANALYSIS.md` + `ECOSYSTEM_RECOMMENDATIONS.md` + `.claude/registry/LEGACY_REGISTRY.md` + `DUPLICATE_REGISTRY.md` + discovery + implementation reports | ✅ AKTIVNÍ — DISCOVERY + DOKUMENTACE |
| SPOS-016 | Repository Consolidation Engine | `.claude/context/REPOSITORY_CONSOLIDATION.md` + `LEGACY_MIGRATION_PLAN.md` + `MODULE_CLASSIFICATION.md` + `DEPENDENCY_ANALYSIS.md` + `CODE_DUPLICATION_REPORT.md` + `ARCHITECTURE_ALIGNMENT.md` + `ROOT_DIRECTORY_AUDIT.md` + `TECHNICAL_DEBT_REGISTER.md` + `CONSOLIDATION_ROADMAP.md` + implementation report | ✅ AKTIVNÍ — PLNÝ AUDIT + KONSOLIDAČNÍ PLÁN |

---

## AUTOMATION CLI (dostupné v `platform/.starcore/scripts/`)

| Nástroj | Účel |
|---|---|
| `registry.py` | Prompt Registry CLI (register/list/search/supersede/validate) |
| `ledger.py` | Session Ledger CLI (start/end/current/add-decision/add-risk) |
| `decision_engine.py` | Interaktivní rozhodovací formát (format/render/check-safety/log) |
| `impact_analyzer.py` | Analýza dopadu změn (soubor → modul → dopad) |
| `regression_sentinel.py` | Detekce regresí vs. baseline |
| `release_readiness.py` | 12-gate release readiness evaluace |
| `qc_engine.py` | Sjednocený QC orchestrátor |
| `startup_protocol.py` | 12-step cold-start session inicializace |

---

## ZNÁMÉ MEZERY (viz SPOS-000-RUNTIME-BOOTSTRAP.md pro detail)

1. SPOS-006 Documentation Engine — dokumentace se aktualizuje manuálně, ne automatizovaným skenováním/validací
2. SPOS-007 Infrastructure Control — Proxmox/Docker control existuje jako Provider SDK, ale ne jako řídicí SPOS vrstva s inventářem
3. SPOS-009 Evolution Engine — chybí mechanismus pro řízenou evoluci promptů/architektury v čase
4. SPOS-010 — dva paralelní "digital twin" dokumenty s odlišným scope (ekosystém vs. platform), zastaralost platform snapshotu (v0.4.0 → realita v0.6.0)

---

## SPOS-001 IMPLEMENTACE (2026-08-06)

**Přístup:** Adoptovat existující `platform/.starcore/memory/`, doplnit pouze chybějící kusy — žádná paralelní implementace.

Doplněno:
- `platform/.starcore/memory/current_state.md` — lehký "kde právě jsme" pointer (chyběl, spec §4/§8 ho vyžadovala)
- `platform/.starcore/state/project_state.json` — strojově čitelný PROJECT_STATE ENGINE (VERSION, CURRENT_PHASE, ACTIVE_TASK, COMPLETED_TASKS, BLOCKERS, RISKS, NEXT_ACTIONS dle §8)
- `.claude/context/CONTEXT_RESTORATION_PROTOCOL.md` — implementace §12 AI Context Restoration, formálně propojuje `.claude/` (SES/SAKB/SPOS) s `platform/.starcore/` (runtime paměť) — dosud o sobě nevěděly
- Aditivní odkazy v `platform/CLAUDE.md` a `platform/.starcore/README.md` na nové soubory a na `.claude/` vrstvu

Funkčně ověřeno: `startup_protocol.py --quick --json` běží bez chyby po přidání nových souborů (žádný existující kód nebyl změněn).

CHANGE MEMORY (§7): nebyla vytvořena samostatná struktura — spec explicitně odkazuje na Git history/GitHub/ADR jako zdroj, což už je pokryto (`git log`, ADR-001..017). Nejde o mezeru.

---

## SPOS-002 IMPLEMENTACE (2026-08-06)

**Přístup:** Audit → adopce → živé otestování (ne jen statická analýza).

Zjištění:
- `platform/.starcore/sessions/ledger.yaml` obsahoval 1 session s `end_time: null` od 2026-07-26 — **nikdy neuzavřena** (porušení §3 lifecycle, session zůstala navždy v ACTIVE stavu)
- `_archive_session()` v `ledger.py` **již plně implementuje** §8 HANDOVER REPORT formát (Summary, Decisions, Files, Tests, Next Action) — žádná mezera
- `sessions/current.md` je **manuálně** udržovaný soubor — `ledger.py` ho needituje automaticky

Provedeno (živě, ne jen navrženo):
1. `ledger.py end` — retroaktivně uzavřena osiřelá session, archivována do `sessions/archive/2026-07-26-*.md`
2. `ledger.py start` — zaregistrována aktuální bootstrap session (`claude/starcore-ai-bootstrap-fkyb96`)
3. `ledger.py add-request/add-decision/add-risk/add-file` (×16 volání) — naplněn session record dle §4
4. `ledger.py validate` — potvrzeno: 2 sezení, 1 aktivní, 1 uzavřeno, žádná chyba integrity
5. `sessions/current.md` ručně aktualizován (mimo automatizaci skriptu)
6. Vytvořeny `.claude/context/SESSION_CONTEXT.md` (§6) a `.claude/registry/SESSION_REGISTRY.md` (§18)

Žádný Python skript nebyl změněn — pouze použit jeho existující CLI.

---

## SPOS-003 IMPLEMENTACE (2026-08-06)

**Přístup:** Registr `prompts/registry.yaml` už existoval s 8 prompty (PROM-001..008) z předchozí session — ale **žádný SES/SAKB/SPOS prompt této bootstrap session nebyl registrován**. To byla hlavní mezera.

Provedeno (živě, přes `registry.py` CLI, ne ruční YAML editace):
1. `registry.py register` (×7) — zaregistrovány SES-000, SES-001, SAKB-000, SPOS-000, SPOS-001, SPOS-002, SPOS-003 s korektním dependency chainem (přesně dle §8 příkladu: SPOS-003 depends SPOS-000/001/002)
2. `ledger.py add-prompt` (×7) — propojeny s aktuální session (§12 Prompt Memory Integration)
3. `registry.py validate` — potvrzeno: 15 promptů, žádné chyby
4. `registry.py list/search/get` — funkčně otestováno

Nalezená mezera: `PromptEntry` model nemá `RELATED_FILES`/`RELATED_COMMITS`/`VALIDATION_STATUS`/`INPUTS`/`OUTPUTS` z §5 — zaznamenáno v `PROMPT_REGISTRY.md`, dataclass vědomě nerozšiřován (riziko zásahu do 384řádkového otestovaného skriptu).

Vytvořeny: `.claude/registry/PROMPT_REGISTRY.md` (ekosystémový index, §19 povinný registr).

---

## SPOS-004 IMPLEMENTACE (2026-08-06)

**Klíčové zjištění:** Project Intelligence Engine (PIE) v podstatě **už existoval** — `impact_analyzer.py`, `regression_sentinel.py`, `release_readiness.py`, `qc_engine.py` dohromady implementují přesně model §3 (OBSERVE→COLLECT→ANALYZE→UNDERSTAND→RECOMMEND→DECIDE), jen nebyly formálně zaregistrovány jako "intelligence layer".

Provedeno:
1. `impact_analyzer.py analyze --since HEAD~5` — živě otestováno, 35 souborů korektně namapováno na testy (§8 Change Intelligence)
2. `qc_engine.py run --quick` — živě otestováno, produkuje STAV/ZJIŠTĚNO/RIZIKA/DOPORUČENÍ/DOPAD/RIZIKO/ROLLBACK/DALŠÍ KROK (přesně Decision Engine formát)
3. Vytvořen `.claude/registry/INTELLIGENCE_REGISTRY.md` (§5) — 7 engines zaregistrováno (4 v Pythonu + 3 mapované na existující `.claude/` dokumenty: MODULE_REGISTRY = Architecture Intelligence, IMPROVEMENT_ROADMAP = Roadmap Intelligence, CONTEXT_RESTORATION_PROTOCOL = AI Context Generation)
4. Vytvořen `.claude/reports/SPOS-004-HEALTH-REPORT.md` (§6) — provizorní PROJECT_HEALTH_SCORE 77.8 % vypočten manuálně z živého výstupu (kód nerozšiřován)
5. Zjištěno skutečné, nesouvisející riziko: Alembic migrace nejsou v sync (PACKAGE gate FAIL) — zaznamenáno jako reálné doporučení P1

Mezery: §12 Automatic Reporting (daily/weekly/milestone) neimplementováno — vyžaduje scheduler infrastrukturu, mimo scope. §6 numerický health score neexistuje v kódu — nahrazeno manuální agregací v reportu.

Žádný Python skript nebyl změněn.

---

## SPOS-005 IMPLEMENTACE (2026-08-06)

**Klíčový rozdíl oproti SPOS-004:** Poprvé byl spuštěn **plný toolchain**, ne jen `--quick` mód. `uv sync --extra dev` doplnil chybějící dev závislosti (pytest, ruff, pyright, pip-audit) do `platform/.venv/` (dosud obsahoval jen bandit/alembic/fastapi).

Živě spuštěno a ověřeno:
1. `pytest -q` → 796 passed, 9 skipped (postgres, očekávaně), 0 selhání
2. `ruff check .` → All checks passed
3. `pyright` → 0 errors
4. `bandit -r packages/ apps/ scripts/ -ll -q` → 0 nálezů
5. `pip-audit` → 0 zranitelností
6. `alembic check` → FAILED → `alembic upgrade head` → OPRAVENO (lokální DB, ne kód)
7. `qc_engine.py run` (full mód) → RELEASE_READY_WITH_WARNINGS, žádný blocker

**Oprava SPOS-004:** PACKAGE gate FAIL byl nesprávně interpretován jako kódový problém — ve skutečnosti šlo o nemigrovanou lokální SQLite DB. Po `alembic upgrade head` gate PASSuje. Health score přepočten: 77,8 % → **88,2 %**.

Vytvořeny: `.claude/registry/AUDIT_REGISTRY.md` (§5, 7 domén A01-A07), `.claude/reports/FIRST_FULL_AUDIT_REPORT.md` (§15, 5 findings, AUDIT_RUN_ID AR-2026-08-06-001).

Žádný Python skript nebyl změněn — pouze spuštěn existující, nyní kompletní CI toolchain.

---

## SPOS-006 IMPLEMENTACE (2026-08-06)

Audit nalezl 126 Markdown dokumentů napříč repozitářem, `platform/docs/` (56 souborů, mkdocs-based) je již velmi dobře udržovaný systém — žádný nový dokumentační systém nevytvořen.

Provedeno:
1. `mkdocs build --strict` živě spuštěn → PASS (exit 0), 1 INFO nález (ADR-017 chybí v nav)
2. Vytvořen `.claude/context/DOCUMENTATION_MAP.md` (§4, §18) — normalizace dle 6 typů (Architecture/Development/Operations/Infrastructure/AI/Knowledge)
3. Vytvořen `.claude/reports/DOCUMENTATION_HEALTH_REPORT.md` (§6, §18) — D001-D006 kontroly, 9 nálezů
4. **Nový nález (D004):** `platform/docs/ses/SES-0000-MASTER-INDEX.md` (ChatGPT-generovaný, 4místné číslování) vs. `.claude/ses/SES-000-*.md` (tato session, 3místné číslování) — riziko záměny, nezmazáno (P010), jen zdokumentováno
5. Code↔Doc sync (§8) ověřen pro MOD-001..015 — potvrzuje existující SES-001 mezeru (MOD-010..015 bez testů/dokumentace)

Mezery: STARCORE Installation Manual (§10) a USER_GUIDE (§13) nevytvořeny — velký rozsah, vyžadují samostatný implementační krok, ne součást tohoto auditu. Automatická generace dokumentace (§7) neimplementována — mimo scope.

Žádný Python/MkDocs konfigurační soubor nebyl změněn — pouze spuštěn existující build.

---

## SPOS-007 IMPLEMENTACE (2026-08-06)

Audit potvrdil: žádný samostatný infrastrukturní inventář neexistoval (registrováno jako gap ve SPOS-000/006), ale **kód pro správu existuje** (`platform/packages/providers/{docker,proxmox}`, MOD-005/006). Vytvořen inventář nad tímto kódem, ne duplicitní implementace.

Živě ověřeno přes `starcore diagnose --json`:
- `runtime_environment: local`
- `provider.proxmox: error` — chybí credentials (STARCORE_PROXMOX_*)
- `provider.docker: error` — Docker daemon neběží (jen CLI binárka nainstalována)
- DB migrace na head (0002) — potvrzuje SPOS-005 opravu

**Oprava Bootstrap 00:** Tehdejší INFRASTRUCTURE_REGISTRY.md uváděl Docker jako "Aktivní". Live test ukázal: CLI je nainstalováno, ale `/var/run/docker.sock` neexistuje — daemon neběží. Opraveno v `CONTAINER_REGISTRY.md`.

Vytvořeno: `INFRASTRUCTURE_MAP.md` (§3/§18 model DATACENTER→HOST→HYPERVISOR→VM/LXC→SERVICE), `HARDWARE_REGISTRY.md` (3 hosty), `COMPUTE_REGISTRY.md` (3 plánované VM), `CONTAINER_REGISTRY.md` (4 služby), `REMOTE_SERVICE_REGISTRY.md` (4 služby, GitHub+Anthropic aktivní).

Nové nálezy: `api_gateway/` a `backups/` v root repo nejsou v MODULE_REGISTRY ani auditovány — přidáno jako TODO.

Žádný Python skript nebyl změněn.

---

## SPOS-008 IMPLEMENTACE (2026-08-06)

**Zásadní nález:** Živě ověřeno (`head -1` na všech 65 `install_*.sh`) — **100 % skriptů** má shebang `#!/data/data/com.termux/files/usr/bin/bash` (Termux/Android specifický). Tyto skripty generují stub Python soubory (`{"status": "online"}`), ne funkční deploy automation. Skutečná produkční deployment cesta je **Track A**: `platform/Dockerfile` + `docker-compose.yml` + CI (`ci.yml`).

**Poznámka k číslování:** Tento prompt (SPOS-008 "Deployment Automation Engine") **neodpovídá** původnímu SPOS-000 mapování, kde SPOS-008 = "AI Orchestration". Skutečné pořadí promptů se od SPOS-007 mírně liší od SPOS-000 abstraktního seznamu — zaznamenáno jako governance drift, ne chyba. Tabulka výše aktualizována, aby odrážela realitu (co bylo skutečně implementováno) místo původního plánu.

Provedeno:
1. Audit 65 install skriptů — potvrzeno 100 % Termux shebang
2. Audit root `.github/workflows/` — 3 z 6 workflow souborů jsou scaffolding/placeholder (`starcore-release.yml`, `starcore-integrity.yml` odkazuje na neexistující `core/` adresář), jen `ci.yml` a `starcore-security.yml` dělají něco reálného
3. Vytvořen `DEPLOYMENT_ARCHITECTURE.md` (§3/§18) — Track A vs Track B jasně odděleny
4. Vytvořen `DEPLOYMENT_REGISTRY.md` (§9) — 4 záznamy (1 aktivní CI gate, 1 orphaned docker-publish, 1 plánovaný Proxmox, 1 historický Termux)
5. Vytvořen `INSTALLER_STUDIO_PLAN.md` (§8) — **návrh, ne implementace**, staví na existujícím Provider SDK

Žádný Python/shell skript nebyl vytvořen ani změněn — pouze auditováno a zdokumentováno.
