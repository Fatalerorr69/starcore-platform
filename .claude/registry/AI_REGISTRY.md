# AI REGISTRY

Aktualizováno: 2026-08-06 | Standard: SES-001

Formát dle SES-001 §13: MODEL, PROVIDER, PURPOSE, VERSION, RESOURCE REQUIREMENTS, INTEGRATION, STATUS.

---

## AI OPERÁTOR

| Položka | Hodnota |
|---|---|
| Model | Claude Sonnet 4.6 (claude-sonnet-4-6) |
| Role | Hlavní AI Engineering Agent |
| Prostředí | Claude Code Remote (cloud container) |
| Branch | `claude/starcore-ai-bootstrap-fkyb96` |
| Session | 2026-08-06 |

---

## AI PROVIDER INTEGRACE (Platform)

| Provider | Konfigurace | Status |
|---|---|---|
| Anthropic Claude | `STARCORE_ANTHROPIC_API_KEY` | Aktivní (volitelné) |
| OpenAI-compatible | `STARCORE_AI_PROVIDER=openai-compatible` + `STARCORE_AI_BASE_URL` | Aktivní (Ollama, vLLM, LM Studio) |

---

## LLM MODELY (plánované)

| Model | Provider | Purpose | Version | Resource Req. | Integration | Status |
|---|---|---|---|---|---|---|
| Claude (Sonnet/Opus) | Anthropic | Blueprint generation, AI agent operator | claude-sonnet-4-6 | Cloud API, žádné lokální zdroje | `platform/packages/ai` (AIProvider ABC) | AKTIVNÍ |
| llama3.2 | Ollama | Obecné AI úkoly | latest | ~4-8GB VRAM/RAM | OpenAI-compatible endpoint | PLÁNOVÁNO |
| mistral | Ollama | Kód a analýza | latest | ~4-8GB VRAM/RAM | OpenAI-compatible endpoint | PLÁNOVÁNO |
| nomic-embed-text | Ollama | Embedding pro Qdrant RAG | latest | ~1GB RAM | Qdrant integrace (MOD-102) | PLÁNOVÁNO |
| codestral | Ollama | Code generation | latest | ~8-16GB VRAM | OpenAI-compatible endpoint | PLÁNOVÁNO |

---

## AI AGENTI (platforma)

| Agent | Adresář | Účel | Status |
|---|---|---|---|
| Blueprint Generator (AGENT-001) | `platform/packages/ai` | YAML blueprint z přirozeného jazyka | AKTIVNÍ |
| Task Scheduler (AGENT-002) | `platform/packages/orchestrator` | Async TaskGraph execution | AKTIVNÍ |
| QC Engine (AGENT-003) | `platform/.starcore/scripts/qc_engine.py` | CI orchestration + Project Intelligence | AKTIVNÍ |
| Impact Analyzer (AGENT-004) | `platform/.starcore/scripts/impact_analyzer.py` | Code change impact analysis | AKTIVNÍ |
| Kernel Agent (AGENT-S02) | `agents/kernel/` | JSON stub (ne reálný agent) | STUB |
| Mission Planner (AGENT-S03) | `agents/missions/` | JSON stub (ne reálný agent) | STUB |

Detail: `.claude/registry/AGENT_REGISTRY.md` (SPOS-011)

---

## WORKFLOW

| Workflow | Typ | Status |
|---|---|---|
| AI Blueprint Generation | Platform API (`POST /ai/generate-blueprint`) | AKTIVNÍ |
| GitHub Actions CI | Automatické testy na každý PR | AKTIVNÍ |
| Security Scanning | Bandit + gitleaks + pip-audit | AKTIVNÍ |
| n8n Automation | Workflow orchestrace | PLÁNOVÁNO |
