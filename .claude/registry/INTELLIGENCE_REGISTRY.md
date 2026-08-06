# INTELLIGENCE REGISTRY

Standard: SPOS-004 §5 | Aktualizováno: 2026-08-06

Project Intelligence Engine (PIE) **již existoval** v `platform/.starcore/scripts/` — audit potvrdil, že implementuje přesně model §3 (OBSERVE→COLLECT→ANALYZE→UNDERSTAND→RECOMMEND→DECIDE), jen nebyl formálně registrován jako "intelligence layer". Zaregistrováno, ne duplikováno.

---

## ENGINES

### ENGINE-001 — Change Impact Analyzer
```yaml
name: impact_analyzer.py
purpose: "Mapuje git diff -> modul -> impact kategorie -> ovlivnene testy (SPOS-004 §8 Change Intelligence)"
inputs: "git diff / --since <ref>, cesta k souboru"
outputs: "FILE/MODULE/CATEGORIES/DEPENDENTS/TESTS tabulka, evidence-based (zadna spekulace)"
status: ACTIVE
verified: "Zive spusteno pres impact_analyzer.py analyze --since HEAD~5 — spravne zmapovalo 35 zmenenych souboru na ovlivnene testy"
```

### ENGINE-002 — Regression Sentinel
```yaml
name: regression_sentinel.py
purpose: "Detekce driftu v 7 dimenzich vs. baseline (SPOS-004 §7 Risk Detection — technical debt/architectural drift)"
inputs: "state/regression_baseline.json, aktualni stav repo (testy, API routes, CLI, config, ADR, workflows, lock)"
outputs: "PASS/FAIL/UNKNOWN per dimenze"
status: ACTIVE
```

### ENGINE-003 — Release Readiness Engine
```yaml
name: release_readiness.py
purpose: "12-gate hodnoceni pripravenosti (SPOS-004 §6 Project Health Model: BUILD/TEST/SECURITY/DEPENDENCIES/PACKAGE/ARTIFACT/DOCUMENTATION/GITHUB/GOVERNANCE/DEPLOYMENT/BACKUP/RECOVERY)"
inputs: "CI vysledky, git stav, dependency audit"
outputs: "PASS/FAIL/UNKNOWN/NOT_APPLICABLE per gate, RELEASE_VERDICT"
status: ACTIVE
```

### ENGINE-004 — QC Orchestrator
```yaml
name: qc_engine.py
purpose: "Sjednocuje ENGINE-001..003 do jednoho Decision-Engine-formatovaneho reportu (STAV/ZJISTENO/RIZIKA/DOPORUCENI/DOPAD/RIZIKO/ROLLBACK/DALSI KROK)"
inputs: "vyvolava ostatni 3 engines"
outputs: "Komplexni QC report, Czech, s ACTION_REQUIRED menu"
status: ACTIVE
verified: "Zive spusteno pres qc_engine.py run --quick — viz .claude/reports/SPOS-004-HEALTH-REPORT.md"
```

### ENGINE-005 — Architecture Intelligence (mapováno na existující registr)
```yaml
name: MODULE_REGISTRY.md
purpose: "COMPONENTS/DEPENDENCIES/RELATIONSHIPS/OWNERSHIP/STATUS (SPOS-004 §9)"
inputs: "manualni audit + SES-001 gap analyza"
outputs: ".claude/registry/MODULE_REGISTRY.md — 15 modulu, MOD-001..015"
status: ACTIVE (mimo platform/.starcore/, v .claude/ governance vrstve)
```

### ENGINE-006 — Roadmap Intelligence (mapováno na existující dokument)
```yaml
name: IMPROVEMENT_ROADMAP.md
purpose: "CURRENT_STATE/TARGET_STATE/GAPS/PRIORITY/NEXT_BEST_ACTION (SPOS-004 §10)"
inputs: "Bootstrap 00 discovery"
outputs: ".claude/reports/IMPROVEMENT_ROADMAP.md — 5 fazi"
status: ACTIVE
```

### ENGINE-007 — AI Context Generation (mapováno na existující protokol)
```yaml
name: CONTEXT_RESTORATION_PROTOCOL.md + SESSION_CONTEXT.md
purpose: "AI_CONTEXT_PACKAGE (PROJECT STATE/RELEVANT FILES/RISKS/RECOMMENDATIONS) pro cold-start (SPOS-004 §11)"
inputs: "Digital Twin, memory, session ledger"
outputs: ".claude/context/CONTEXT_RESTORATION_PROTOCOL.md, .claude/context/SESSION_CONTEXT.md"
status: ACTIVE (vytvořeno v SPOS-001/002, nyní formálně součástí PIE)
```

---

## ZNÁMÉ MEZERY

| # | Mezera (§) | Popis | Rozhodnutí |
|---|---|---|---|
| 1 | §6 PROJECT_HEALTH_SCORE | Žádný jednotný číselný skóre v kódu — jen PASS/FAIL/UNKNOWN per gate | Vypočten manuálně v `.claude/reports/SPOS-004-HEALTH-REPORT.md` z live výstupu, metodika transparentně zdokumentována — kód NEROZŠÍŘEN |
| 2 | §12 Automatic Reporting (DAILY/WEEKLY/MILESTONE) | Žádný scheduler — engines běží jen on-demand | Zaznamenáno jako gap, mimo scope (vyžaduje cron/GitHub Actions infrastrukturu — kandidát na budoucí SPOS krok) |

Žádný Python skript nebyl změněn — všechny 4 engines použity živě přes existující CLI.
