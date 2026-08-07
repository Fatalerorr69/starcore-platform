# AI PIPELINES

Standard: SPOS-011 §11 | Aktualizováno: 2026-08-07

Dokumentace existujících CI/AI pipeline a návrh rozšíření.

---

## EXISTUJÍCÍ PIPELINE (aktivní)

### PIPELINE-001 — CI Validation (GitHub Actions)

```
Repository Push / PR
        ↓
[ci.yml — GitHub Actions]
        ↓
    uv sync --extra dev
        ↓
    pytest -q (796 passed)
        ↓
    ruff check .
        ↓
    pyright
        ↓
    bandit -r ...
        ↓
    pip-audit
        ↓
    alembic check
        ↓
    [PASS → merge allowed] | [FAIL → merge blocked]
```

**Status:** AKTIVNÍ ✅ | Soubor: `.github/workflows/ci.yml`

### PIPELINE-002 — Blueprint Execution Pipeline

```
Natural Language Description
        ↓
[POST /ai/generate-blueprint]
        ↓
AIProvider.generate_blueprint_yaml()
  → Anthropic API / OpenAI-compat
        ↓
BlueprintLoader.load_from_string()
  → Pydantic validation
        ↓
planner.py → TaskGraph (DAG)
        ↓
Scheduler.execute(graph)
  → asyncio.gather() per wave
        ↓
BaseProvider.execute() per task
  (Docker / Proxmox / Kubernetes)
        ↓
event_bus.emit("run.completed")
```

**Status:** AKTIVNÍ (kód) / providers offline ⚠️ | Soubory: `packages/ai/` + `packages/orchestrator/` + `packages/blueprints/`

### PIPELINE-003 — Security Scan (GitHub Actions)

```
Repository Push
        ↓
[starcore-security.yml]
        ↓
gitleaks secret scan
        ↓
[PASS → OK] | [FAIL → alert]
```

**Status:** AKTIVNÍ ✅ | Soubor: `.github/workflows/starcore-security.yml`

---

## PLÁNOVANÁ PIPELINE (SPOS-011 §11)

### PIPELINE-010 — Automation Pipeline

```
Repository Change (git push)
        ↓
Impact Analysis (impact_analyzer.py) [EXISTS ✅]
        ↓
Documentation Check (mkdocs build --strict) [EXISTS ✅]
        ↓
Tests (pytest) [EXISTS ✅]
        ↓
Audit (qc_engine.py) [EXISTS ✅]
        ↓
Release Check (release_readiness.py) [EXISTS ✅]
        ↓
Commit (git commit) [MANUÁLNÍ]
        ↓
Knowledge Update (knowledge/ sync) [CHYBÍ — žádná automatizace]
        ↓
Digital Twin Update (DIGITAL_TWIN.md) [CHYBÍ — manuální]
```

**Status:** ČÁSTEČNÁ — všechny kroky mají implementaci, ale nejsou zřetězeny do jednoho workflow.

**Gap:** Chybí orchestrátor který by spouštěl tyto kroky v pořadí automaticky.
**Odhad:** MEDIUM effort — shell/Python wrapper nad existujícími nástroji, bez nového frameworku.

---

## PIPELINE STATUS PŘEHLED

| Pipeline | Status | Automatická | Poznámka |
|---|---|---|---|
| CI Validation | ✅ AKTIVNÍ | ANO (GitHub Actions) | Nejspolehlivější pipeline |
| Blueprint Execution | ⚠️ KÓDOVĚ AKTIVNÍ | ANO (API endpoint) | Providers offline |
| Security Scan | ✅ AKTIVNÍ | ANO (GitHub Actions) | Gitleaks |
| Automation Pipeline | ⏳ PLÁNOVANÁ | NE (manuální kroky) | Chybí orchestrátor |
| RAG Indexing | ❌ CHYBÍ | N/A | Qdrant neexistuje |
| Knowledge Sync | ❌ CHYBÍ | N/A | Ruční tvorba profilů |
| Deployment (Proxmox) | ❌ BLOKOVANÁ | N/A | Chybí credentials |
