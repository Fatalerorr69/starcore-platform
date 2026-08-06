# SES-001 — STARCORE TECHNICAL ENGINEERING STANDARD

```yaml
Document ID:     SES-001
Title:           STARCORE Technical Engineering Standard
Version:         1.0.0
Status:          ACTIVE — APPROVED
Parent:          SES-000 (Engineering Constitution)
Repository:      Fatalerorr69/starcore-platform
Branch:          claude/starcore-ai-bootstrap-fkyb96
Date Created:    2026-08-06
```

SES-000 definuje principy. SES-001 definuje technický standard: strukturu repository, návrh modulů, závislosti, API, testování, dokumentaci, CI/CD, infrastrukturu, AI workflow, registry a údržbu.

---

## 1. ENGINEERING MODEL (6 vrstev)

| Vrstva | Obsah | STARCORE mapování |
|---|---|---|
| LAYER 0 — Governance | SES, ADR, standardy, pravidla změn | `.claude/ses/`, `platform/docs/adr/` |
| LAYER 1 — Core Platform | Aplikace, knihovny, API, business logika | `platform/packages/core`, `platform/apps/cli` |
| LAYER 2 — Providers | Docker, Proxmox, K8s, cloud, AI | `platform/packages/providers`, `platform/packages/ai` |
| LAYER 3 — Automation | CLI, workflow, skripty, deployment | `platform/apps/cli`, `.github/workflows/`, install skripty |
| LAYER 4 — Knowledge | Dokumentace, registry, znalostní DB | `platform/docs/`, `.claude/registry/`, `knowledge/` |
| LAYER 5 — Infrastructure | Servery, VM, kontejnery, edge | Proxmox (cílový), `agents/`, Termux skripty |

---

## 2. REPOSITORY STANDARD — SOULAD

Doporučený model dle SES-001:
```
apps/ | packages/ | services/ | infrastructure/ | automation/ | docs/ | tests/ | scripts/ | .github/ | .claude/ | README.md
```

**Zjištěný stav:**

| Očekáváno | Realita v repo | Soulad |
|---|---|---|
| `apps/`, `packages/` | existuje uvnitř `platform/apps/`, `platform/packages/` | ✅ (o úroveň hlouběji) |
| `tests/` | `platform/tests/` | ✅ |
| `docs/` | `platform/docs/` | ✅ |
| `.github/` | root `.github/` (sdílené) | ✅ |
| `.claude/` | root `.claude/` | ✅ |
| `infrastructure/` | NEEXISTUJE | ❌ GAP |
| `services/` | NEEXISTUJE (funkčnost je v `packages/providers`) | ⚠️ jiný název, funkčně pokryto |
| Root bez aplikační logiky | Root obsahuje 64 bash install skriptů + `agents/`, `runtime/`, `knowledge/`, `security/`, `intelligence/`, `ai_core/`, `control_center/`, `automation/` | ❌ PORUŠENÍ PRAVIDLA §3 |

**Rozhodnutí (viz RULE 5 SES-000 — vícevariantní volba):**

| Varianta | Výhody | Nevýhody | Rizika | Doporučení |
|---|---|---|---|---|
| A) Ponechat `platform/` jako jediný zdroj aplikační logiky, ostatní root adresáře postupně migrovat/archivovat | Čistý soulad se SES-001 §3 | Velký refaktoring, riziko rozbití runtime state | Ztráta historie, přerušení skriptů | ✅ DOPORUČENO — postupně, ne najednou |
| B) Deklarovat root adresáře (`agents/`, `runtime/`, ...) jako LAYER 5 Infrastructure/Automation výjimku | Rychlé, bez rizika | Repo zůstává nekonzistentní | Standard SES-001 §3 zůstává formálně porušen | Dočasné řešení |
| C) Nedělat nic | Nulové úsilí | Trvalý nesoulad, technický dluh roste | Vysoké — SES-001 §3 explicitně zakazuje | ❌ NEDOPORUČENO |

→ **Přijato: Varianta B jako dočasný stav + Varianta A jako cílový stav v roadmapě (Fáze 6, viz níže).** Vyžaduje explicitní schválení uživatele před fyzickým přesunem souborů (P010).

---

## 3. MODULE STANDARD

Povinná metadata pro každý modul: `MODULE_ID, MODULE_NAME, PURPOSE, OWNER, STATUS, DEPENDENCIES, INPUTS, OUTPUTS, INTERFACES, TEST_STRATEGY, DOCUMENTATION`.

**Stav:** `MODULE_REGISTRY.md` (vytvořen v Bootstrap 00) obsahuje ID/název/adresář/status/verzi/testy/dokumentaci, ale chybí PURPOSE/OWNER/DEPENDENCIES/INPUTS/OUTPUTS/INTERFACES/TEST_STRATEGY na úrovni jednotlivých modulů → **rozšířeno v této revizi** (viz `MODULE_REGISTRY.md` update níže).

---

## 4. NAMING CONVENTIONS — SOULAD

| Konvence | Standard | Zjištěný stav | Soulad |
|---|---|---|---|
| Python | `snake_case` | `platform/packages/*` dodržuje | ✅ |
| Classes | `PascalCase` | `BaseProvider`, `TaskGraph`, `ProviderRegistry` | ✅ |
| Constants | `UPPER_CASE` | `HTTP_REQUEST_DURATION_SECONDS` | ✅ |
| Files | `lowercase_with_underscore` | dodržuje | ✅ |
| Directories | `lowercase` | dodržuje | ✅ |
| Docs | `UPPERCASE-WITH-DASHES.md` | mix (`README.md`, `CHANGELOG.md` = OK; ADR soubory `ADR-001-blueprint-...md` = OK) | ✅ |
| Root install skripty | `install_6BX18_master_consolidator.sh` (mix čísel/verzí) | ⚠️ nekonzistentní, ale mimo `packages/`/`apps/` scope | Nízké riziko |

**Závěr:** Platform kód je plně v souladu. Root install skripty jsou legacy a mimo přísný scope SES-001 §5 (nejsou to moduly, jsou to jednorázové instalátory).

---

## 5. DEPENDENCY MANAGEMENT — SOULAD

| Požadavek | Stav |
|---|---|
| pip-audit | ✅ v CI (`ci.yml`) |
| Dependabot | ❌ CHYBÍ — žádný `.github/dependabot.yml` |
| SBOM | ❌ CHYBÍ |
| Lockfile (uv.lock) | ✅ existuje, kontrolován v CI (`uv lock --check`) |

**GAP:** Dependabot a SBOM nejsou nastaveny. → přidáno do Implementation Plan.

---

## 6. API STANDARD — SOULAD

| Požadavek | Stav |
|---|---|
| Verzované API (`/api/v1/`) | ❌ CHYBÍ — aktuální routery (`ai`, `auth`, `blueprints`, `diagnostics`, `providers`, `runs`, `ws`) nejsou prefixované verzí |
| Dokumentované endpointy | ✅ FastAPI auto-generuje OpenAPI/Swagger |
| Input/output schema | ✅ Pydantic modely |
| Error handling | ✅ HTTPException, JSONResponse |

**GAP — API verzování chybí.** Toto je MAJOR/ARCHITECTURAL změna (breaking change pro existující klienty) → vyžaduje ADR + explicitní schválení, **není implementováno automaticky** (P010).

---

## 7. TESTING STANDARD — SOULAD

| Požadavek | Stav |
|---|---|
| Unit testy | ✅ |
| Integration testy | ✅ (`tests/integration/` dle README) |
| Regression testy | ✅ (implicitně přes 100% coverage floor) |
| PASS: testy, lint, security, docs | ✅ vše v CI |

**Plně v souladu.**

---

## 8. DOCUMENTATION STANDARD — SOULAD

Platform (`platform/docs/`): README, Architecture, Usage (CLI/API docs), Examples — ✅ přítomno.
Root repository moduly (`agents/`, `knowledge/`, `security/`, ...): ❌ bez README/dokumentace → potvrzuje GAP z `DOCUMENTATION_AUDIT.md` (Bootstrap 00).

---

## 9. CI/CD STANDARD — SOULAD

Pipeline `ci.yml`: Format (ruff format) → Lint (ruff check) → Type check (pyright) → Security (pip-audit, bandit, gitleaks) → Test (pytest) → Migration check (alembic).

| Fáze SES-001 | Realita | Soulad |
|---|---|---|
| FORMAT | ruff format --check | ✅ |
| LINT | ruff check | ✅ |
| TEST | pytest --cov-fail-under=100 | ✅ |
| SECURITY | pip-audit, bandit, gitleaks | ✅ |
| BUILD | (implicitní přes uv sync) | ⚠️ není explicitní build step/artifact |
| DOCUMENTATION CHECK | ❌ CHYBÍ — žádný krok validující MkDocs build nebo doc freshness | GAP |

---

## 10. INFRASTRUCTURE STANDARD — SOULAD

IaC preferováno: Docker Compose, Terraform, Ansible, skripty.

| Nástroj | Stav |
|---|---|
| Docker Compose | ✅ existuje `platform/docker-compose.yml` (dev), AI Stack compose PLÁNOVÁN (Bootstrap 00 Fáze 2) |
| Terraform | ❌ nepoužito |
| Ansible | ❌ nepoužito, PLÁNOVÁNO (Bootstrap 00 Fáze 3) |
| Rollback možnost | ✅ Proxmox snapshoty (`starcore snapshot`) |

---

## 11. PROXMOX STANDARD

`INFRASTRUCTURE_REGISTRY.md` (Bootstrap 00) již obsahuje HOST/VM/services strukturu — **v souladu s formátem SES-001 §12**, ale VM jsou zatím PLÁNOVANÉ (žádný reálný Proxmox přístup v tomto prostředí).

---

## 12. AI PLATFORM STANDARD

`AI_REGISTRY.md` (Bootstrap 00) obsahuje MODEL/PROVIDER/PURPOSE/STATUS — **v souladu s formátem SES-001 §13**. Rozšířeno o RESOURCE REQUIREMENTS a INTEGRATION pole v této revizi.

---

## 13. SECURITY STANDARD — SOULAD

| Požadavek | Stav |
|---|---|
| Dependency Audit | ✅ pip-audit |
| Secrets Detection | ✅ gitleaks |
| Permission Review | ⚠️ manuální, není automatizováno |
| Network Review | ⚠️ manuální |
| Access Review | ⚠️ manuální (single API key model, ADR-012) |
| Žádné hardcoded secrets | ✅ `.gitignore` obsahuje `.venv/`, žádné `.env` commitnuté |

---

## IMPLEMENTATION PLAN (co se implementuje TEĎTO, co čeká na schválení)

### Implementováno v této revizi (dokumentační, nedestruktivní)
- [x] `MODULE_REGISTRY.md` rozšířen o PURPOSE/OWNER/DEPENDENCIES/INTERFACES
- [x] `AI_REGISTRY.md` rozšířen o RESOURCE REQUIREMENTS/INTEGRATION
- [x] `DIGITAL_TWIN.md` aktualizace (SES-001 stav)
- [x] Tento SES-001 dokument s gap analýzou

### Vyžaduje explicitní schválení uživatele (P010 — Human Approval Gate)
| Změna | Klasifikace | Důvod čekání |
|---|---|---|
| API verzování `/api/v1/` | MAJOR/ARCHITECTURAL | Breaking change, nutný ADR |
| Přesun root modulů (`agents/`, `knowledge/`...) pod `packages/`/`services/` | ARCHITECTURAL | Vysoké riziko rozbití runtime state |
| Dependabot config | MINOR | Nízké riziko, ale mění CI chování — navrhnout, počkat na potvrzení |
| SBOM generování | MINOR | Nový CI krok |
| Documentation-check CI krok (mkdocs build --strict) | MINOR | Nový CI krok, může selhat na existující docs |

---

## QUALITY DEFINITION — AKTUÁLNÍ STAV

| Kritérium | Stav |
|---|---|
| Architecture | ⚠️ ČÁSTEČNĚ COMPLIANT (root layer mimo standard, dokumentováno jako výjimka) |
| Tests | ✅ PASS (601 testů, 100% coverage) |
| Documentation | ⚠️ CURRENT pro `platform/`, CHYBÍ pro root moduly |
| Security | ✅ VALIDATED (CI gates aktivní) |
| Infrastructure | ⚠️ REPRODUCIBLE pro platform dev; Proxmox cíl zatím NEPROKÁZÁN |
| Knowledge | ✅ REGISTERED (`.claude/registry/` kompletní) |

**Celkové hodnocení: ČÁSTEČNÝ SOULAD.** Platform vrstva (`platform/`) je plně v souladu se SES-001. Root ekosystémová vrstva vyžaduje buď formální výjimku, nebo postupnou migraci (viz §2 rozhodnutí).
