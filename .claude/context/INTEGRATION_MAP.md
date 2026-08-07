# INTEGRATION MAP

Standard: SPOS-012 §17 | Aktualizováno: 2026-08-07

Vizuální mapa integrace všech vrstev STARCORE ekosystému.

---

## LAYER OVERVIEW

```
╔══════════════════════════════════════════════════════════════╗
║                    GOVERNANCE LAYER                          ║
║  .claude/ses/ | .claude/sakb/ | .claude/spos/               ║
║  .claude/registry/ | .claude/context/DIGITAL_TWIN.md        ║
╠══════════════════════════════════════════════════════════════╣
║                    KNOWLEDGE LAYER                           ║
║  knowledge/ (6/22 profiles) | .claude/sakb/                 ║
║  ADR (17 docs) | platform/docs/ (56 docs)                   ║
╠══════════════════════════════════════════════════════════════╣
║                    AI ORCHESTRATION LAYER                    ║
║  packages/ai/ (AIProvider ABC + 2 providers)                ║
║  packages/orchestrator/ (Scheduler + TaskGraph)             ║
║  packages/blueprints/ (YAML → TaskGraph pipeline)           ║
╠══════════════════════════════════════════════════════════════╣
║                    PLATFORM CORE LAYER                       ║
║  packages/core/ (FastAPI + Auth + Events + Metrics)         ║
║  packages/provider_sdk/ (BaseProvider + Registry)           ║
║  apps/cli/ (Typer CLI)                                       ║
╠══════════════════════════════════════════════════════════════╣
║                    PROVIDER LAYER                            ║
║  providers/docker/ [OFFLINE]                                 ║
║  providers/proxmox/ [OFFLINE — no credentials]              ║
║  providers/kubernetes/ [OFFLINE — no cluster]               ║
╠══════════════════════════════════════════════════════════════╣
║                    INFRASTRUCTURE LAYER                      ║
║  SQLite (dev DB) [AKTIVNÍ]                                   ║
║  PostgreSQL [PLÁNOVANÝ — scaffold]                           ║
║  Redis [PLÁNOVANÝ — scaffold]                                ║
║  NATS [PLÁNOVANÝ — scaffold]                                 ║
╠══════════════════════════════════════════════════════════════╣
║                    CI/CD LAYER                               ║
║  .github/workflows/ci.yml [AKTIVNÍ]                         ║
║  .github/workflows/starcore-security.yml [AKTIVNÍ]          ║
║  platform/.github/ [ORPHANED]                               ║
╠══════════════════════════════════════════════════════════════╣
║                    EXTERNAL SERVICES                         ║
║  Anthropic API [AKTIVNÍ — klíč z env]                       ║
║  GitHub API [AKTIVNÍ — CI + MCP]                            ║
║  Ollama/OpenAI-compat [PLÁNOVANÝ]                           ║
║  Proxmox VE [PLÁNOVANÝ]                                      ║
╠══════════════════════════════════════════════════════════════╣
║                    EDGE / ANDROID LAYER                      ║
║  65 install_*.sh [STUB — Termux shebangs]                   ║
║  runtime/android/ [STUB — ~/STARCORE path]                  ║
║  installers/android/ [STUB]                                  ║
╚══════════════════════════════════════════════════════════════╝
```

---

## INTEGRATION STATUS MATRIX

| Source | Target | Status | IF-ID |
|---|---|---|---|
| CLI | Platform API | ✅ AKTIVNÍ | IF-001 |
| Platform API | Blueprint Engine | ✅ AKTIVNÍ | IF-002 |
| Blueprint Engine | Orchestrator | ✅ AKTIVNÍ | IF-003 |
| Orchestrator | ProviderRegistry | ✅ AKTIVNÍ (kód) | IF-004 |
| ProviderRegistry | Docker | ❌ OFFLINE | IF-005 |
| ProviderRegistry | Proxmox | ❌ OFFLINE | IF-006 |
| Platform API | AI Provider | ✅ AKTIVNÍ | IF-007 |
| AI Provider | Anthropic | ✅ AKTIVNÍ (klíč) | IF-008 |
| AI Provider | OpenAI-compat | ❌ SERVER OFFLINE | IF-009 |
| Orchestrator | EventBus | ✅ AKTIVNÍ | IF-010 |
| Platform API | SQLite | ✅ AKTIVNÍ | IF-011 |
| Plugin System | ProviderRegistry | ✅ AKTIVNÍ | IF-012 |
| GitHub | CI Pipeline | ✅ AKTIVNÍ | IF-013 |
| QC Engine | CI Tools | ✅ AKTIVNÍ | IF-014 |
| Session Ledger | Filesystem | ✅ AKTIVNÍ | IF-015 |
| Claude Code | GitHub MCP | ✅ AKTIVNÍ (session) | IF-016 |
| platform/.github/ | GitHub Actions | ❌ ORPHANED | IF-B01..B03 |

---

## INTEGRATION GAP SUMMARY

```yaml
fully_integrated: 12 interfaces (IF-001..012, 014..015)
ai_infrastructure_gap:
  description: "AI providers existují ale žádný provider server neběží (Ollama/vLLM offline)"
  impact: "Blueprint generation přes OpenAI-compat není možná; pouze Anthropic (pokud API key nastaven)"

infrastructure_gap:
  description: "Docker/Proxmox/K8s providers offline — blueprint execution nefunguje end-to-end"
  impact: "TaskGraph se vytvoří ale provider.execute() selže"

message_bus_gap:
  description: "EventBus je in-process only — žádná cross-service komunikace"
  impact: "Škálování na microservices vyžaduje NATS (scaffold)"

rag_gap:
  description: "Žádná vector DB — knowledge nelze prohledávat přes embeddings"
  impact: "RAG nepoužitelný; znalosti jsou jen statické Markdown soubory"

github_orphan:
  description: "platform/.github/ není čteno GitHubem"
  impact: "Dependabot alerts neaktivní; SBOM negenerován"
```
