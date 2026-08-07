# AI HEALTH REPORT

Standard: SPOS-011 §13 | Datum: 2026-08-07 | Run ID: AI-HEALTH-2026-08-07-001

---

## PROVIDER HEALTH

| Provider | Status | Latency | Dostupnost | Poznámka |
|---|---|---|---|---|
| Anthropic API | NEOVĚŘENO (žádná live volání) | N/A | API klíč z env ✅ | Kód funkční (AnthropicProvider) |
| OpenAI-compat | OFFLINE | N/A | Žádný server | Kód funkční, server neběží |
| Docker | OFFLINE | N/A | Daemon neběží | CLI instalováno, socket neexistuje |
| Proxmox | OFFLINE | N/A | Credentials chybí | Provider kód existuje |
| Kubernetes | OFFLINE | N/A | Žádný cluster | Provider kód existuje |

---

## MEMORY HEALTH

| Vrstva | Status | Poznámka |
|---|---|---|
| Session (current.md) | OK | Aktualizováno v SPOS-002 |
| Ledger (ledger.yaml) | OK | 1 aktivní session, 1 archivovaná |
| Project State (project_state.json) | OK | SPOS-001 addition |
| Memory (current_state.md) | OK | SPOS-001 addition |
| Snapshot (project_snapshot.md) | ZASTARALÝ | v0.4.0 vs realita v0.6.0 |
| Digital Twin | OK | Aktualizováno po každém SPOS |

---

## TOOL HEALTH

| Nástroj | Status | Last Verified |
|---|---|---|
| pytest | OK (796 passed) | 2026-08-06 |
| ruff | OK | 2026-08-06 |
| pyright | OK | 2026-08-06 |
| bandit | OK (0 findings) | 2026-08-07 |
| pip-audit | OK (0 CVE) | 2026-08-07 |
| alembic | OK (head = 0002) | 2026-08-06 |
| ledger.py | OK | 2026-08-06 |
| registry.py | OK | 2026-08-06 |
| qc_engine.py | OK | 2026-08-06 |
| impact_analyzer.py | OK | 2026-08-06 |
| release_readiness.py | OK | 2026-08-06 |
| starcore diagnose | OK | 2026-08-06 |
| mkdocs build --strict | OK | 2026-08-06 |

---

## WORKFLOW HEALTH

| Workflow | Status | Poznámka |
|---|---|---|
| CI Validation (ci.yml) | AKTIVNÍ | 796 tests, 0 failures |
| Security Scan (gitleaks) | AKTIVNÍ | CI-only |
| Blueprint Execution | KÓDOVĚ OK / OFFLINE | providers nedostupné |
| Session Lifecycle | AKTIVNÍ | ledger.py funkční |
| Context Restoration | AKTIVNÍ | protokol dokumentován |

---

## AGENT HEALTH

| Agent | Status | Health |
|---|---|---|
| AGENT-001 Blueprint Generator | AKTIVNÍ | OK (kód), NEOVĚŘENO (live volání) |
| AGENT-002 Task Scheduler | AKTIVNÍ | OK (kód), OFFLINE (providers) |
| AGENT-003 QC Engine | AKTIVNÍ | OK — 88.2% health score |
| AGENT-004 Impact Analyzer | AKTIVNÍ | OK — 35 souborů mapped |
| AGENT-010..012 | PLÁNOVANÍ | N/A |

---

## AI HEALTH SCORE

```yaml
score_methodology: "Vážený průměr dle kategorií"
categories:
  code_quality:    weight: 30%  score: 100%  reason: "pytest/ruff/pyright vše PASS"
  security:        weight: 20%  score: 75%   reason: "0 CVE, 0 bandit; workflow permissions chybí"
  ai_providers:    weight: 20%  score: 30%   reason: "kód OK, žádný provider online"
  memory:          weight: 15%  score: 85%   reason: "struktury OK, 1 zastaralý snapshot"
  knowledge:       weight: 15%  score: 40%   reason: "6/22 tech profiles, žádný RAG"

composite_score: "(0.30*100) + (0.20*75) + (0.20*30) + (0.15*85) + (0.15*40)"
composite_score_value: "30 + 15 + 6 + 12.75 + 6 = 69.75% ≈ 70%"
assessment: ČÁSTEČNĚ_ZDRAVÝ

note: |
  Nízké skóre AI providers (30%) je způsobeno absencí živé infrastruktury (Proxmox/Docker/Ollama).
  Kódová základna AI orchestrace je v dobrém stavu. Skóre poroste při nasazení ai-core VM.
```

---

## ERRORS + WARNINGS

```yaml
errors: []

warnings:
  - "W001: Docker daemon offline (socket /var/run/docker.sock neexistuje)"
  - "W002: Proxmox credentials chybí (STARCORE_PROXMOX_* env vars)"
  - "W003: Žádný AI provider neověřen live (žádné testovací API volání)"
  - "W004: project_snapshot.md zastaralý (v0.4.0)"
  - "W005: 11/16 GitHub workflows bez explicitního permissions bloku"

statistics:
  agents_active: 4
  agents_planned: 3
  providers_active_code: 2
  providers_online: 0
  workflows_active: 5
  knowledge_profiles: 6/22
  health_score: "70%"
  last_updated: "2026-08-07"
```
