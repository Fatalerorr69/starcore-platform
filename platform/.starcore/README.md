# .starcore/ — Perzistentní paměť projektu

Tento adresář je **cross-session state layer** pro STARCORE Autonomous Engineering Agent.
Slouží jako sdílená paměť mezi Claude Code sezeními — nové sezení zde najde vše potřebné
pro okamžité převzetí práce bez re-derivace kontextu.

## Struktura

```
.starcore/
  README.md                    — tento soubor; přehled struktury
  memory/
    risks.md                   — kanonický risk register
    user_preferences.md        — preference uživatele a pravidla pro approval
    project_snapshot.md        — klíčová fakta pro cold start
    architecture.md            — referenční přehled architektury
    decisions.md               — pracovní rozhodnutí (pre-ADR)
    known_issues.md            — aktivní známé problémy
    completed_work.md          — záznam dokončené práce
    pending_work.md            — zbývající práce s prioritami
  sessions/
    current.md                 — human-readable session ledger (reference)
    ledger.yaml                — machine-readable session ledger (zdroj pravdy)
    archive/                   — archiv ukončených sezení (Markdown)
  prompts/
    registry.yaml              — katalog registrovaných promptů (PROM-xxx)
    master/                    — master provozní prompty
    audits/                    — audit prompty
    implementation/            — implementační prompty
    recovery/                  — recovery prompty
  reports/
    latest/                    — nejnovější vygenerované reporty
    archive/                   — archiv reportů
  scripts/
    models.py                  — datové modely (PromptEntry, SessionEntry, CheckResult)
    registry.py                — Prompt Registry CLI
    ledger.py                  — Session Ledger CLI
    decision_engine.py         — Interactive Decision Engine CLI
    impact_analyzer.py         — Change Impact Analyzer (soubor → modul → dopad)
    regression_sentinel.py     — Regression Sentinel (detekce regresí vs baseline)
    release_readiness.py       — Release Readiness Engine (12 gates)
    qc_engine.py               — QC Orchestrátor (sjednocený report)
    startup_protocol.py        — Startup Protocol (12-step session init, Czech report)
    tests/                     — standalone testy pro scripts/ (171 testů)
  state/
    regression_baseline.json   — sentinel baseline (testy, coverage, vulns, sentinel)
    release.md                 — stav release readiness
```

## Pravidla pro práci s tímto adresářem

1. **Nikdy neskladuj secrets/credentials** — ani redacted ani placeholder formy
2. **`sessions/ledger.yaml`** je machine-readable zdroj pravdy; `sessions/current.md` je human-readable reference
3. **`state/regression_baseline.json` aktualizuj** po každém úspěšném průchodu CI gates
4. **`memory/pending_work.md` aktualizuj** při každé změně scope (přidání/dokončení práce)
5. **`memory/risks.md`** je kanonický risk register — `reports/*.md` jsou historické archivy
6. Prompt registry spravuj přes CLI: `uv run python .starcore/scripts/registry.py`
7. Session ledger spravuj přes CLI: `uv run python .starcore/scripts/ledger.py`
8. Po každém auditu/implementaci/selhání použij **Decision Engine formát** (viz `memory/decision_engine.md`)

## Cold-start protokol (pro nová sezení)

1. Přečti `memory/project_snapshot.md` — klíčová fakta
2. Načti předchozí sezení: `uv run python .starcore/scripts/ledger.py current`
3. Přečti `memory/pending_work.md` — co zbývá udělat
4. Přečti `memory/risks.md` — aktivní rizika
5. Ověř git stav (`git status`, `git log --oneline -5`)
6. Spusť smoke-test (`uv run pytest -q --tb=no 2>&1 | tail -3`)
7. Zahaj nové sezení: `uv run python .starcore/scripts/ledger.py start --session-id "..." --branch "..." --head "..."`
8. Teprve pak začni pracovat

## Automation CLI

```bash
# Prompt Registry
uv run python .starcore/scripts/registry.py list
uv run python .starcore/scripts/registry.py list --status ACTIVE
uv run python .starcore/scripts/registry.py get PROM-001
uv run python .starcore/scripts/registry.py search "timeout"
uv run python .starcore/scripts/registry.py register --name "..." --type MASTER --purpose "..."
uv run python .starcore/scripts/registry.py update PROM-001 --status DEPRECATED
uv run python .starcore/scripts/registry.py supersede PROM-001 --by PROM-007
uv run python .starcore/scripts/registry.py versions PROM-001
uv run python .starcore/scripts/registry.py validate

# Session Ledger
uv run python .starcore/scripts/ledger.py list
uv run python .starcore/scripts/ledger.py current
uv run python .starcore/scripts/ledger.py start --session-id "session-id" --branch "branch" --head "abc1234"
uv run python .starcore/scripts/ledger.py end --next-action "Příští akce"
uv run python .starcore/scripts/ledger.py add-decision "Použít X místo Y"
uv run python .starcore/scripts/ledger.py add-risk R-001
uv run python .starcore/scripts/ledger.py add-test --passed 569 --failed 0 --coverage 100.0
uv run python .starcore/scripts/ledger.py reconstruct SESSION_ID
uv run python .starcore/scripts/ledger.py validate

# Decision Engine
uv run python .starcore/scripts/decision_engine.py format             # prázdná šablona
uv run python .starcore/scripts/decision_engine.py render --file r.yaml
cat report.yaml | uv run python .starcore/scripts/decision_engine.py render --file -
uv run python .starcore/scripts/decision_engine.py parse-choice "Varianta 2"
uv run python .starcore/scripts/decision_engine.py check-safety "git push --force"
uv run python .starcore/scripts/decision_engine.py log --decision "Zvolena varianta 1"
uv run python .starcore/scripts/tests/test_decision_engine.py        # 49 testů

# QC Engines
uv run python .starcore/scripts/impact_analyzer.py analyze
uv run python .starcore/scripts/impact_analyzer.py analyze --since HEAD~1
uv run python .starcore/scripts/impact_analyzer.py module SOUBOR

uv run python .starcore/scripts/regression_sentinel.py check
uv run python .starcore/scripts/regression_sentinel.py diff
uv run python .starcore/scripts/regression_sentinel.py update   # jen po CI průchodu

uv run python .starcore/scripts/release_readiness.py evaluate --quick
uv run python .starcore/scripts/release_readiness.py evaluate
uv run python .starcore/scripts/release_readiness.py gate SECURITY

uv run python .starcore/scripts/qc_engine.py run --quick
uv run python .starcore/scripts/qc_engine.py run --impact
uv run python .starcore/scripts/tests/test_qc_engines.py        # 68 testů
```

## Odkaz v CLAUDE.md

Viz sekci "Persistent project memory" v kořenovém CLAUDE.md.
