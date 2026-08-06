# FIRST FULL AUDIT REPORT — STARCORE Platform

Standard: SPOS-005 §6, §8 | Datum: 2026-08-06 | Prostředí: Claude Code Remote (platform/.venv nově synchronizován přes `uv sync --extra dev`)

Toto je první **plně živě ověřený** audit celého toolchainu v tomto bootstrapu — na rozdíl od SPOS-004 Health Reportu (který používal `--quick` mód a manuální odhady), zde byly skutečně spuštěny pytest, ruff, pyright, bandit, pip-audit a alembic.

---

## AUDIT_RUN_ID: AR-2026-08-06-001

```yaml
date: 2026-08-06
type: FULL
version: "platform v0.6.0"
result: RELEASE_READY_WITH_WARNINGS
severity: LOW (žádný blocker)
```

---

## A02 — CODE QUALITY AUDIT (živě ověřeno)

| Nástroj | Výsledek |
|---|---|
| pytest | **796 passed, 9 skipped** (postgres testy, očekávaně — `STARCORE_TEST_POSTGRES_URL` nenastaveno), 77.9s |
| ruff check | **All checks passed!** |
| pyright | **0 errors, 0 warnings, 0 informations** |

**Nález FINDING-001:** Regression Sentinel hlásí `test_count 801 → 805 (Δ+4)` oproti baseline — WARNING, ne FAIL. Baseline (`state/regression_baseline.json`) byl zaznamenán při 801 testech; teď je 805. Toto je pravděpodobně environmentální drift (ne kód této session — žádný testovací soubor nebyl v této session vytvořen ani upraven), ale je potřeba lidské rozhodnutí, zda baseline aktualizovat.

---

## A03 — SECURITY AUDIT (živě ověřeno, částečně)

| Nástroj | Výsledek |
|---|---|
| bandit `-r packages/ apps/ scripts/ -ll -q` | **0 nálezů** |
| pip-audit | **0 zranitelností** (`starcore-platform` sám vynechán — není na PyPI, očekávané) |
| gitleaks | **NEOVĚŘENO** — binárka není dostupná v tomto prostředí; běží pouze jako GitHub Action |

---

## A06 — DEPENDENCY AUDIT (živě ověřeno)

`uv sync --extra dev` proběhl bez chyb. `uv.lock` konzistentní s `pyproject.toml` (potvrzeno Regression Sentinel). pip-audit čistý (viz A03).

---

## A07 — ARCHITECTURE AUDIT

| Kontrola | Výsledek |
|---|---|
| GOVERNANCE gate (release_readiness.py) | ✓ PASS |
| ADR count | 17 (beze změny) |
| **FINDING-002** (existující, ze SES-001) | MOD-010..015 (agents/, knowledge/, security/, intelligence/, control_center/, ai_core/) nemají testy ani dokumentaci dle SES-001 §3-4 standardu |

---

## KRITICKÝ NÁLEZ — VYŘEŠENO ŽIVĚ BĚHEM TOHOTO AUDITU

**FINDING-003 (vyřešeno):** SPOS-004 Health Report zaznamenal `PACKAGE gate FAIL — Alembic migrace nejsou v sync` jako P1 riziko. Při tomto plném auditu bylo zjištěno, že šlo o **lokálně nemigrovanou SQLite databázi** (`data/starcore.db`, gitignored, environmentální artefakt), ne o skutečný nesoulad modelů a migrací.

```
uv run alembic check   → FAILED: Target database is not up to date.
uv run alembic upgrade head   → 2 migrace aplikovány (0001, 0002)
uv run alembic check   → No new upgrade operations detected. (OK)
```

Žádné trackované soubory nebyly změněny (`git status` čistý po opravě — `data/` je v `.gitignore`). **Oprava SPOS-004 nálezu:** PACKAGE gate ve skutečnosti PASSuje po plném `qc_engine.py run` (bez `--quick`).

---

## VÝSLEDNÝ PROJECT_HEALTH_SCORE (přepočet, nahrazuje provizorní SPOS-004 hodnotu)

| Kategorie | PASS | FAIL | UNKNOWN | N/A |
|---|---|---|---|---|
| Regression Sentinel (7 dim.) | 6 | 0 | 0 (1 WARNING — test drift) | — |
| Release Readiness (12 gates) | 9 | 0 | 2 (BUILD, SECURITY) | 1 (ARTIFACT) |
| **CELKEM** | **15** | **0** | **2** | **1** |

**Score: 15/17 = 88.2 %** (zlepšeno z provizorních 77,8 % po plném běhu a opravě Alembic stavu). BUILD a SECURITY gates zůstávají UNKNOWN i v plném módu — vyžadují pravděpodobně Docker build test a plnou security review proceduru mimo `qc_engine.py` scope.

---

## FINDINGS SUMMARY (dle §8 formátu)

| Finding ID | Titul | Kategorie | Risk | Status |
|---|---|---|---|---|
| FINDING-001 | Test count drift (801→805) vs baseline | Code Quality | NÍZKÉ | OPEN — čeká na rozhodnutí (aktualizovat baseline?) |
| FINDING-002 | MOD-010..015 bez testů/dokumentace | Architecture | STŘEDNÍ | OPEN (existující ze SES-001) |
| FINDING-003 | Alembic PACKAGE gate FAIL | Package | ~~VYSOKÉ~~ | **VYŘEŠENO** — lokální DB migrace, ne kódový problém |
| FINDING-004 | Dependabot/SBOM orphaned v `platform/.github/` | Security/CI | STŘEDNÍ | OPEN (ze SES-001, čeká na schválení přesunu) |
| FINDING-005 | BUILD a SECURITY gates trvale UNKNOWN i v plném módu | Release Readiness | NÍZKÉ | OPEN — vyžaduje vyšetření mimo scope tohoto auditu |

---

## DOPORUČENÍ

| Priorita | Doporučení |
|---|---|
| P2 | Rozhodnout: aktualizovat `regression_baseline.json` na 805 testů (pokud je nárůst legitimní) |
| P2 | Přesunout `platform/.github/dependabot.yml` + `docker-publish.yml` do root `.github/` (FINDING-004) |
| P3 | Vyšetřit proč BUILD/SECURITY gates zůstávají UNKNOWN i mimo `--quick` mód |
| P3 | Naplánovat audit MOD-010..015 (FINDING-002) jako samostatný DISCOVERY úkol |

---

## ROLLBACK

Všechny provedené kontroly byly read-only vůči trackovanému kódu. Jediná stavová změna (`alembic upgrade head`) se týkala pouze lokální, gitignored SQLite databáze — bez dopadu na repozitář.
