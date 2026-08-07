# INTEGRATION HEALTH

Standard: SPOS-012 §14 | Aktualizováno: 2026-08-07

Zdravotní report integrace STARCORE ekosystému.

---

## SKÓRE (SPOS-012 §14)

```yaml
score_date: "2026-08-07"
methodology: "Váhovaný průměr dle kategorií — vychází výhradně z Discovery"

integration_score:
  description: "Procento aktivních rozhraní z celkových"
  formula: "active_interfaces / total_interfaces = 16/23 = 69.6%"
  value: 70%

dependency_score:
  description: "Absence cyklických závislostí + zdravý dependency DAG"
  factors: "0 circular deps, pyright 0 errors, clean module hierarchy"
  value: 95%

architecture_score:
  description: "Dodržení SES-001 standardu + ADR coverage"
  factors: "platform/ = full compliance; ecosystem = Variant B exception"
  value: 75%

interface_score:
  description: "Plně dokumentovaná rozhraní bez broken/orphaned"
  formula: "active / (active + broken + offline) = 16/23 = 70%"
  value: 70%

provider_score:
  description: "Providers s online status"
  formula: "online / total = 2 / 6 = 33%"
  note: "2 online: Anthropic (klíč z env), GitHub; 4 offline: Docker, Proxmox, K8s, OpenAI-compat"
  value: 33%

tool_score:
  description: "Dostupné a funkční nástroje"
  formula: "active / total = 14 / 19 = 74%"
  value: 74%

infrastructure_score:
  description: "Infrastruktura provozuschopná"
  factors: "SQLite OK; Docker/Proxmox/Redis/NATS/Qdrant = offline/planned"
  formula: "active / total = 1 / 7 = 14%"
  value: 14%

overall_health:
  weights: {integration: 20%, dependency: 15%, architecture: 15%, interface: 15%, provider: 15%, tool: 10%, infrastructure: 10%}
  calculation: "(70*0.20) + (95*0.15) + (75*0.15) + (70*0.15) + (33*0.15) + (74*0.10) + (14*0.10)"
  value: "14 + 14.25 + 11.25 + 10.5 + 4.95 + 7.4 + 1.4 = 63.75% ≈ 64%"
  assessment: ČÁSTEČNĚ_ZDRAVÝ
  note: "Nízké skóre způsobeno offline infrastructure (Docker/Proxmox/NATS/Redis). Kódová báze je zdravá."
```

---

## ZDRAVÍ PER VRSTVA

| Vrstva | Score | Status | Klíčový problém |
|---|---|---|---|
| Governance | 95% | ✅ ZDRAVÉ | 1 zastaralý snapshot (project_snapshot.md v0.4.0) |
| Knowledge | 65% | ⚠️ ČÁSTEČNÉ | 6/22 profiles, žádný RAG |
| AI Orchestration | 80% | ✅ ZDRAVÉ | Kód OK; providers offline |
| Platform Core | 90% | ✅ ZDRAVÉ | 796 testů, 0 failures |
| Provider Layer | 33% | ❌ SLABÉ | 3/3 providers offline |
| Infrastructure | 20% | ❌ SLABÉ | Jen SQLite online |
| CI/CD | 80% | ✅ ZDRAVÉ | starcore-integrity.yml rozbité |
| External Services | 40% | ⚠️ ČÁSTEČNÉ | Anthropic+GitHub ok; ostatní offline |
| Edge/Android | 5% | ❌ STUB | 100% Termux stubs |

---

## KOMPONENT HEALTH

| Komponenta | Health | Poznámka |
|---|---|---|
| Platform API | OK | FastAPI + auth + metrics |
| Blueprint Engine | OK | Validated, tested |
| Orchestrator | OK (kód) / DEGRADED (providers offline) | Scheduler funguje, providers ne |
| Provider SDK | OK (kód) | Registry funguje |
| Docker Provider | OFFLINE | Daemon socket neexistuje |
| Proxmox Provider | OFFLINE | Credentials chybí |
| Kubernetes Provider | OFFLINE | Žádný cluster |
| AI Provider (Anthropic) | OK | klíč z env |
| AI Provider (OpenAI-compat) | OFFLINE | Žádný server |
| CLI | OK | Typer CLI funkční |
| QC Engine | OK | 88.2% project health |
| CI Pipeline | OK | 796 pass, 0 fail |
| Security Scan | OK | gitleaks aktivní |
| Session Ledger | OK | Funkční |
| SQLite DB | OK | head = 0002 |

---

## NEJVĚTŠÍ RIZIKA

```yaml
RISK-001:
  severity: STŘEDNÍ
  area: Infrastructure
  description: "Všechny 3 infrastrukturní providers offline — end-to-end blueprint execution nefunkční"
  mitigation: "Nasazení ai-core VM s Proxmox credentials"
  impact: "Core product feature (blueprint execution) nefunkční v tomto prostředí"

RISK-002:
  severity: STŘEDNÍ
  area: GitHub CI
  description: "starcore-integrity.yml odkazuje na neexistující root core/ — workflow fail"
  mitigation: "Opravit nebo archivovat workflow"
  impact: "CI noise, špatný zdravotní stav CI palubní desky"

RISK-003:
  severity: NÍZKÁ
  area: Knowledge
  description: "16/22 technology profiles chybí — RAG nepoužitelný"
  mitigation: "Postupná tvorba profilů"
  impact: "AI agent bez kontextu pro 16 technologií"

RISK-004:
  severity: NÍZKÁ
  area: GitHub
  description: "platform/.github/ orphaned — Dependabot neaktivní"
  mitigation: "Přesunout do root .github/"
  impact: "Dependency security alerts neaktivní"
```
