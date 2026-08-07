# INTEGRATION RECOMMENDATIONS

Standard: SPOS-012 §15 | Aktualizováno: 2026-08-07

Doporučení pro zlepšení integrace STARCORE ekosystému. Vychází výhradně z Discovery auditu a INTEGRATION_HEALTH.md.

---

## PRIORITIZACE (dle závažnosti)

```
CRITICAL  → Blokuje core product feature
HIGH      → Významný dopad na delivery
MEDIUM    → Zlepšení stability / observability
LOW       → Tech debt, nice-to-have
FUTURE    → Strategické — vyžaduje infrastrukturu
```

---

## CRITICAL

### REC-001 — Zprovoznit alespoň 1 infra provider pro end-to-end testing

```yaml
id: REC-001
priority: CRITICAL
area: Infrastructure / Provider Layer
current_state: "3/3 providers offline (Docker, Proxmox, K8s) — blueprint execution selže na provider.execute()"
recommendation: "Zprovoznit DockerProvider jako první — Docker daemon dostupný lokálně nebo v CI"
rationale: "Jedná se o core product feature. TaskGraph se validuje, ale nelze vykonat žádnou task."
effort: NÍZKÁ  # Docker socket je nejjednodušší path
impact: KRITICKÝ
action_items:
  - "Spustit Docker daemon v CI (github actions services: docker)"
  - "Ověřit DockerProvider.connect() v integration testu"
  - "Přidat smoke test: execute simple container task via blueprint"
blocking: ["WF-002 Blueprint Execution", "IF-005 Orchestrator→Docker"]
```

### REC-002 — Opravit starcore-integrity.yml workflow

```yaml
id: REC-002
priority: CRITICAL
area: CI/CD
current_state: "starcore-integrity.yml odkazuje na neexistující adresář core/ — workflow fail při každém push"
recommendation: "Archivovat nebo opravit workflow — odebrat reference na core/, přesměrovat na platform/"
rationale: "CI noise maskuje skutečné failures. Integrity check je governance requirement."
effort: NÍZKÁ
impact: STŘEDNÍ
action_items:
  - "Nahradit 'core/' za 'platform/' v starcore-integrity.yml"
  - "Nebo: archivovat workflow jako .disabled a vytvořit nový správný"
  - "Ověřit, že workflow prochází na branch claude/starcore-ai-bootstrap-fkyb96"
blocking: ["IF-013 GitHub→CI Pipeline", "CI dashboard accuracy"]
```

---

## HIGH

### REC-003 — Přesunout platform/.github/ do root .github/

```yaml
id: REC-003
priority: HIGH
area: CI/CD / GitHub
current_state: "platform/.github/ je ORPHANED — GitHub nečte workflows z podadresáře"
affected_interfaces: ["IF-B01", "IF-B02", "IF-B03"]
recommendation: "Sloučit platform/.github/ do root .github/ nebo archivovat"
rationale: "Dependabot alerts neaktivní, SBOM negenerován. Security posture snížen."
effort: NÍZKÁ
impact: STŘEDNÍ
action_items:
  - "Zkopírovat relevantní config z platform/.github/dependabot.yml do .github/dependabot.yml"
  - "Zkopírovat SBOM workflow do .github/workflows/"
  - "Archivovat platform/.github/ (nebo smazat po sloučení)"
  - "Ověřit Dependabot aktivaci přes GitHub Security tab"
blocking: ["RISK-004 z INTEGRATION_HEALTH.md"]
```

### REC-004 — Přidat event persistence (EventBus → storage)

```yaml
id: REC-004
priority: HIGH
area: AI Orchestration / Observability
current_state: "EventBus je in-process only — events se nezaznamenaují po restartu; run_logger zachytává jen run.completed"
recommendation: "Implementovat event persistence: zápis events do SQLite (short-term) nebo Redis (production)"
rationale: "Debuggování asynchronních blueprint runs je obtížné bez event logu. SQLite je již aktivní."
effort: STŘEDNÍ
impact: VYSOKÝ
action_items:
  - "Přidat EventStore třídu (wraps EventBus.subscribe pro všechny events)"
  - "Persist events do SQLite tabulky 'events' (event, payload, timestamp)"
  - "Alembic migration pro novou tabulku"
  - "Expozice přes GET /runs/{run_id}/events endpoint"
blocking: ["Debugging blueprint execution failures", "Audit trail"]
```

### REC-005 — Implementovat OpenAI-compat provider pro lokální LLM

```yaml
id: REC-005
priority: HIGH
area: AI Provider Layer
current_state: "OpenAICompatProvider existuje (httpx), ale žádný Ollama/vLLM server neběží"
recommendation: "Přidat Ollama do docker-compose.yml jako volitelný service (profile: ai-local)"
rationale: "Snižuje závislost na Anthropic API key. Umožňuje offline development a testing."
effort: NÍZKÁ
impact: VYSOKÝ
action_items:
  - "Přidat service ollama do docker-compose.yml pod profilem 'ai-local'"
  - "Přidat OPENAI_COMPAT_BASE_URL=http://ollama:11434/v1 do .env.example"
  - "Přidat smoke test: OpenAICompatProvider.generate_blueprint_yaml() s mock serverem"
  - "Dokumentovat v platform/docs/providers.md"
blocking: ["IF-009 AI Provider→OpenAI-compat"]
```

---

## MEDIUM

### REC-006 — Aktualizovat regression_baseline.json

```yaml
id: REC-006
priority: MEDIUM
area: Quality / CI
current_state: "regression_baseline.json uvádí 801 testů; skutečný stav je 805 testů (drift 4 testy)"
recommendation: "Aktualizovat baseline na 805 testů po ověření CI pass"
rationale: "Drift způsobuje false alarms v QC Engine. Snadná oprava."
effort: MINIMÁLNÍ
impact: NÍZKÝ
action_items:
  - "Spustit 'python -m pytest --co -q | wc -l' pro aktuální count"
  - "Aktualizovat platform/.starcore/memory/regression_baseline.json"
  - "Commitnout jako součást maintenance commitu"
```

### REC-007 — Standardizovat API error responses

```yaml
id: REC-007
priority: MEDIUM
area: API / Platform Core
current_state: "API vrací různé formáty chyb — některé endpointy používají detail: str, jiné strukturované ErrorModel"
recommendation: "Vytvořit centrální ErrorResponse Pydantic model, použít v exception handlers"
rationale: "Konzistentní API contract. IF-001 CLI→Platform API benefit."
effort: STŘEDNÍ
impact: STŘEDNÍ
action_items:
  - "Definovat ErrorResponse(code: str, message: str, detail: Any | None) v packages/core/models.py"
  - "Registrovat @app.exception_handler pro HTTPException a ValidationError"
  - "Aktualizovat API_REGISTRY.md se standardní error schema sekcí"
  - "Přidat testy pro error response format"
```

### REC-008 — Přidat health check pro AI providers

```yaml
id: REC-008
priority: MEDIUM
area: AI Orchestration / Observability
current_state: "GET /diagnostics/health nekontroluje dostupnost AI providers (Anthropic, OpenAI-compat)"
recommendation: "Přidat AI provider health do diagnostics endpoint"
rationale: "Okamžitá viditelnost provider stavu bez debug logů."
effort: NÍZKÁ
impact: STŘEDNÍ
action_items:
  - "Přidat ai_providers sekci do GET /diagnostics/health response"
  - "AnthropicProvider: test s minimálním API voláním nebo client initialization check"
  - "OpenAICompatProvider: HTTP GET na base_url/models"
  - "Přidat timeout 3s pro health checks"
```

### REC-009 — Doplnit chybějící knowledge profiles (16/22)

```yaml
id: REC-009
priority: MEDIUM
area: Knowledge Layer
current_state: "6/22 technology profiles existuje; 16 chybí — RAG nepoužitelný"
recommendation: "Postupná tvorba profilů dle priority technologií"
rationale: "AI agent bez kontextů pro 16 technologií = snížená kvalita blueprint generation."
effort: STŘEDNÍ
impact: STŘEDNÍ
priority_profiles:
  tier1: ["postgresql", "redis", "kubernetes", "github-actions"]
  tier2: ["sqlite", "nats", "alembic", "pydantic"]
  tier3: ["typer", "ruff", "pyright", "bandit", "mkdocs", "pip-audit", "asyncio", "pytest"]
action_items:
  - "Vytvořit knowledge/technologies/infrastructure/postgresql.md"
  - "Vytvořit knowledge/technologies/infrastructure/redis.md"
  - "Vytvořit knowledge/technologies/infrastructure/kubernetes.md"
  - "Pokračovat dle tier priority"
```

---

## LOW

### REC-010 — Přidat GitHub Actions matrix pro Python versions

```yaml
id: REC-010
priority: LOW
area: CI/CD
current_state: "ci.yml testuje pouze na Python 3.11 (nebo aktuální runner default)"
recommendation: "Přidat matrix: [3.11, 3.12] pro ověření kompatibility"
rationale: "Python 3.12 compatibility check. Nízká priorita — kód je moderní."
effort: MINIMÁLNÍ
impact: NÍZKÝ
```

### REC-011 — Přejmenovat nebo archivovat Termux stubs

```yaml
id: REC-011
priority: LOW
area: Repository Hygiene
current_state: "65 install_*.sh a 40+ dalších stub souborů s ~/STARCORE Termux paths v root adresářích"
recommendation: "Přesunout do archive/termux-stubs/ nebo označit jako DEPRECATED v README"
rationale: "Redukce confusion pro nové contributors. Kódová báze je jinak čistá."
effort: NÍZKÁ
impact: NÍZKÝ
action_items:
  - "Vytvořit archive/termux-stubs/ adresář"
  - "git mv installers/ providers/android/ runtime/android/ archive/termux-stubs/"
  - "Přidat DEPRECATED notice do archive/termux-stubs/README.md"
```

### REC-012 — Přidat OpenAPI schema export do CI

```yaml
id: REC-012
priority: LOW
area: Documentation / API
current_state: "OpenAPI schema není automaticky exportováno a verzováno"
recommendation: "Přidat CI step: python -c 'from main import app; import json; print(json.dumps(app.openapi()))' > docs/openapi.json"
rationale: "Statický OpenAPI export pro external integrations a SDK generation."
effort: MINIMÁLNÍ
impact: NÍZKÝ
```

---

## FUTURE (vyžaduje infrastrukturu)

### REC-F01 — Implementovat RAG pipeline (Qdrant + embeddings)

```yaml
id: REC-F01
priority: FUTURE
area: Knowledge / AI
prerequisite: "Qdrant vector DB (docker-compose scaffold), embedding model (Ollama nebo Anthropic)"
recommendation: "Přidat knowledge/embedder.py + Qdrant client pro semantic search přes knowledge profiles"
rationale: "RAG nepoužitelný bez vector DB. Klíčová feature pro SAKB roadmap."
effort: VYSOKÁ
impact: VYSOKÝ
```

### REC-F02 — Nahradit in-process EventBus za NATS

```yaml
id: REC-F02
priority: FUTURE
area: Infrastructure / Messaging
prerequisite: "NATS message bus (docker-compose scaffold)"
recommendation: "Implementovat NATSEventBus wrapper kompatibilní s EventBus API"
rationale: "Škálování na microservices. Current in-process EventBus neumí cross-service komunikaci."
effort: VYSOKÁ
impact: VYSOKÝ
```

### REC-F03 — Automatizovat Digital Twin update

```yaml
id: REC-F03
priority: FUTURE
area: Governance / Automation
prerequisite: "SPOS-013 Automation Engine"
recommendation: "Git hook nebo CI step pro automatický update DIGITAL_TWIN.md při každém commitu"
rationale: "Digital Twin je aktuálně aktualizován ručně — drift risk."
effort: STŘEDNÍ
impact: STŘEDNÍ
```

### REC-F04 — Implementovat PostgreSQL migration (SQLite → PostgreSQL)

```yaml
id: REC-F04
priority: FUTURE
area: Infrastructure / Database
prerequisite: "PostgreSQL service (docker-compose scaffold), environment credentials"
recommendation: "Aktivovat PostgreSQL profile v docker-compose, otestovat Alembic migrations"
rationale: "SQLite je development DB. Production vyžaduje PostgreSQL pro concurrent access."
effort: STŘEDNÍ
impact: VYSOKÝ
```

---

## ROADMAP PŘEHLED

```
Q3 2026 (Immediate):
  ✅ REC-002 — Fix starcore-integrity.yml (LOW effort, CI noise)
  ✅ REC-003 — Merge platform/.github/ (LOW effort, security posture)
  ✅ REC-006 — Update regression baseline (MINIMAL effort)

Q3-Q4 2026 (Sprint):
  🔶 REC-001 — DockerProvider in CI (CRITICAL — unblocks end-to-end)
  🔶 REC-004 — Event persistence via SQLite (HIGH impact)
  🔶 REC-005 — Ollama in docker-compose (HIGH impact, offline dev)
  🔶 REC-008 — AI provider health checks (MEDIUM)
  🔶 REC-009 — Knowledge profiles tier1 (MEDIUM)

Q4 2026 - Q1 2027 (Backlog):
  🔷 REC-007 — Standardize API errors (MEDIUM)
  🔷 REC-010 — Python matrix in CI (LOW)
  🔷 REC-011 — Archive Termux stubs (LOW)
  🔷 REC-012 — OpenAPI export in CI (LOW)

Future (Infrastructure-dependent):
  ⬜ REC-F01 — RAG pipeline (Qdrant)
  ⬜ REC-F02 — NATS EventBus
  ⬜ REC-F03 — Auto Digital Twin
  ⬜ REC-F04 — PostgreSQL production
```

---

## SUMMARY TABULKA

| ID | Priorita | Oblast | Effort | Impact | Status |
|---|---|---|---|---|---|
| REC-001 | CRITICAL | Infrastructure | NÍZKÁ | KRITICKÝ | ⬜ OPEN |
| REC-002 | CRITICAL | CI/CD | NÍZKÁ | STŘEDNÍ | ⬜ OPEN |
| REC-003 | HIGH | GitHub | NÍZKÁ | STŘEDNÍ | ⬜ OPEN |
| REC-004 | HIGH | Orchestration | STŘEDNÍ | VYSOKÝ | ⬜ OPEN |
| REC-005 | HIGH | AI Provider | NÍZKÁ | VYSOKÝ | ⬜ OPEN |
| REC-006 | MEDIUM | Quality | MINIMÁLNÍ | NÍZKÝ | ⬜ OPEN |
| REC-007 | MEDIUM | API | STŘEDNÍ | STŘEDNÍ | ⬜ OPEN |
| REC-008 | MEDIUM | Observability | NÍZKÁ | STŘEDNÍ | ⬜ OPEN |
| REC-009 | MEDIUM | Knowledge | STŘEDNÍ | STŘEDNÍ | ⬜ OPEN |
| REC-010 | LOW | CI/CD | MINIMÁLNÍ | NÍZKÝ | ⬜ OPEN |
| REC-011 | LOW | Hygiene | NÍZKÁ | NÍZKÝ | ⬜ OPEN |
| REC-012 | LOW | API/Docs | MINIMÁLNÍ | NÍZKÝ | ⬜ OPEN |
| REC-F01 | FUTURE | RAG | VYSOKÁ | VYSOKÝ | ⬜ PLANNED |
| REC-F02 | FUTURE | Messaging | VYSOKÁ | VYSOKÝ | ⬜ PLANNED |
| REC-F03 | FUTURE | Governance | STŘEDNÍ | STŘEDNÍ | ⬜ PLANNED |
| REC-F04 | FUTURE | Database | STŘEDNÍ | VYSOKÝ | ⬜ PLANNED |
