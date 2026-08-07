# AAOS RECOMMENDATIONS

Standard: SPOS-014 §12 | Aktualizováno: 2026-08-07

16 doporučení pro zlepšení AAOS zdraví z 38% → 65%+. Vychází z SPOS-014 gap analýzy.

---

## PŘEHLED

```yaml
total_recommendations: 16
quick_wins_xs: 3 (< 1h každý)
quick_wins_s: 5 (1-4h každý)
medium_m: 5 (1-3 dny)
large_l: 3 (1-3 týdny)
projected_health_improvement: "38% → 65%+ (po celém roadmapu)"
```

---

## QUICK WINS — XS (< 1h)

### REC-AAOS-01: max_tokens parametrizace pro AnthropicProvider

```yaml
id: REC-AAOS-01
priority: VYSOKÁ
effort: XS (15 min)
gap: GAP-AAOS-008
description: "Přidat STARCORE_AI_MAX_TOKENS env var do Settings + AnthropicProvider"
implementation:
  - "platform/packages/core/config.py: přidat ai_max_tokens: int = 2000"
  - "platform/packages/ai/providers/anthropic.py: max_tokens=settings.ai_max_tokens"
  - "Žádná breaking change — default hodnota zachována"
health_impact: "+3% Prompt Engine"
```

### REC-AAOS-02: OpenAI-compat timeout parametrizace

```yaml
id: REC-AAOS-02
priority: STŘEDNÍ
effort: XS (15 min)
gap: GAP-AAOS-018
description: "Přidat STARCORE_AI_TIMEOUT env var do Settings + OpenAICompatProvider"
implementation:
  - "platform/packages/core/config.py: přidat ai_timeout: float = 120.0"
  - "platform/packages/ai/providers/openai_compat.py: timeout=settings.ai_timeout"
health_impact: "+2% Provider Routing"
```

### REC-AAOS-03: Dokumentovat a označit stub adresáře

```yaml
id: REC-AAOS-03
priority: STŘEDNÍ
effort: XS (30 min)
gap: GAP-AAOS-005
description: |
  Přidat README.md do agents/, autonomous/, distributed/, ai_runtime/
  s jasným označením: 'STUB — Termux/homelab placeholder, not platform code'
implementation:
  - "Vytvořit agents/README.md, autonomous/README.md, etc."
  - "Volitelně: přesunout stubs do legacy/termux-stubs/ adresáře"
health_impact: "0% health score (clarity improvement, ne funkční)"
note: "Nezbytné aby nový vývoj nevznikal na základě stub false assumptions"
```

---

## QUICK WINS — S (1-4h)

### REC-AAOS-04: RetryConfig napojit na AI providers

```yaml
id: REC-AAOS-04
priority: VYSOKÁ
effort: S (2h)
gap: GAP-AAOS-009
description: |
  packages/provider_sdk/retry.py implementuje RetryConfig + attempt_with_retry.
  Napojit na AnthropicProvider a OpenAICompatProvider pro retry při 429/503.
implementation:
  - "AnthropicProvider.generate_blueprint_yaml(): obalit v attempt_with_retry"
  - "RetryableError při: 429 (rate limit), 503 (service unavailable), httpx.TimeoutException"
  - "Konfigurace: STARCORE_AI_RETRY_MAX_ATTEMPTS (default: 3)"
health_impact: "+8% Provider Routing"
```

### REC-AAOS-05: AI inference Prometheus metriky

```yaml
id: REC-AAOS-05
priority: VYSOKÁ
effort: S (2-3h)
gap: GAP-AAOS-007
description: |
  Přidat AI-specific Prometheus metriky do packages/core/metrics.py:
  - AI_BLUEPRINT_GENERATION_TOTAL (counter: provider, status)
  - AI_BLUEPRINT_GENERATION_DURATION_SECONDS (histogram: provider)
  - AI_BLUEPRINT_VALIDATION_ERRORS_TOTAL (counter: error_type)
implementation:
  - "Přidat countery + histogram do metrics.py"
  - "Instrumentovat packages/ai/generator.py (před a po volání)"
  - "EventBus event: blueprint.generated (pro async tracking)"
health_impact: "+10% Observability"
```

### REC-AAOS-06: 5 nových knowledge profilů

```yaml
id: REC-AAOS-06
priority: STŘEDNÍ
effort: S (2-4h, závisí na hloubce)
gap: GAP-AAOS-010
description: "Doplnit chybějící technology profily (SAKB-000 formát)"
profiles_to_create:
  - "knowledge/technologies/databases/postgresql.md"
  - "knowledge/technologies/messaging/redis.md"
  - "knowledge/technologies/messaging/nats.md"
  - "knowledge/technologies/container/kubernetes.md"
  - "knowledge/technologies/monitoring/prometheus.md"
health_impact: "+8% Knowledge Engine"
```

### REC-AAOS-07: Blueprint gen → auto run pipeline

```yaml
id: REC-AAOS-07
priority: STŘEDNÍ
effort: S (2-3h)
gap: GAP-AAOS-001 (částečně)
description: |
  Jednoduchý pipeline: POST /ai/generate-and-run (blueprint gen + execution v jednom volání)
  Neřeší multi-agent komunikaci ale eliminuje manuální dvě volání.
implementation:
  - "Nový endpoint POST /ai/generate-and-run"
  - "Kombinuje generate_blueprint_yaml() + BlueprintExecutor"
  - "Vrací: yaml + execution_results"
health_impact: "+5% Agent Communication"
```

### REC-AAOS-08: Provider health check před AI voláním

```yaml
id: REC-AAOS-08
priority: STŘEDNÍ
effort: S (1-2h)
gap: GAP-AAOS-004 (částečně), GAP-AAOS-012
description: |
  Přidat async health check před každým generate_blueprint_yaml() voláním.
  Rychlý ping Anthropic nebo OpenAI-compat endpoint — timeout 2s.
  Při selhání: okamžitý popis problému místo pomalého timeout.
health_impact: "+5% Provider Routing"
```

---

## MEDIUM — M (1-3 dny)

### REC-AAOS-09: Mock providers v CI (blueprint end-to-end test)

```yaml
id: REC-AAOS-09
priority: KRITICKÁ
effort: M (1-2 dny)
gap: GAP-AAOS-003
description: |
  Implementovat MockDockerProvider a MockProxmoxProvider pro CI testování.
  Umožní end-to-end blueprint execution testing bez reálné infrastruktury.
implementation:
  - "tests/mocks/mock_docker_provider.py: echo provider (execute → SUCCESS)"
  - "tests/mocks/mock_proxmox_provider.py: echo provider"
  - "pytest fixture: register_mock_providers()"
  - "test_blueprint_e2e.py: full blueprint gen → plan → execute test"
health_impact: "+15% Workflow Orchestration, +5% Agent Coverage"
```

### REC-AAOS-10: BLUEPRINT_SYSTEM_PROMPT parametrizace

```yaml
id: REC-AAOS-10
priority: STŘEDNÍ
effort: M (1 den)
gap: GAP-AAOS-011
description: |
  Refaktorovat BLUEPRINT_SYSTEM_PROMPT na Jinja2 template.
  Parametry: available_providers (docker/proxmox/k8s), user_context (optional),
  knowledge_chunks (RAG injection placeholder).
implementation:
  - "packages/ai/prompts.py: Jinja2 template string"
  - "packages/ai/generator.py: render_system_prompt(providers, context)"
  - "Backward compatible: default params = current behavior"
health_impact: "+5% Prompt Engine, +3% Context Engine"
```

### REC-AAOS-11: NATS integrace (agent message bus základ)

```yaml
id: REC-AAOS-11
priority: VYSOKÁ (strategická)
effort: M (2-3 dny)
gap: GAP-AAOS-001
description: |
  Aktivovat NATS scaffold a integrovat s EventBus.
  Krok 1: EventBus.emit() publishes i do NATS (dual-write)
  Krok 2: AgentBus třída — subscribe/publish přes NATS
  Krok 3: První cross-agent event (QC → CI notification)
implementation:
  - "docker-compose.yml: NATS z profile scaffold → default profile"
  - "packages/core/agent_bus.py: NatsAgentBus (nats-py SDK)"
  - "packages/core/events.py: dual-write EventBus + NATS"
health_impact: "+20% Agent Communication"
prerequisite: "NATS server dostupný (docker-compose)"
```

### REC-AAOS-12: Scheduled QC automation

```yaml
id: REC-AAOS-12
priority: STŘEDNÍ
effort: M (1 den)
gap: GAP-AAOS-015 (related)
description: |
  GitHub Actions workflow: weekly QC run (sobota 06:00 UTC)
  Spustí: qc_engine.py run --quick → výsledky jako GitHub check
  Volitelně: update DIGITAL_TWIN.md automaticky po úspěšném QC
implementation:
  - "Nový .github/workflows/weekly-qc.yml"
  - "qc_engine.py --json output → GitHub step summary"
health_impact: "+5% Self-Optimization"
```

### REC-AAOS-13: Agent Permission Model (základní)

```yaml
id: REC-AAOS-13
priority: STŘEDNÍ
effort: M (1-2 dny)
gap: GAP-AAOS-014, GAP-AAOS-006
description: |
  Definovat permission matrix pro agenty:
  - AGENT-001: read (settings) + call (AI API) only
  - AGENT-002: read (graph) + call (providers) + write (RunRecord)
  - Plugin: read (events) + call (registry.register)
  Implementovat: permission check v BaseProvider.execute()
health_impact: "+10% Security/Sandboxing"
```

---

## LARGE — L (1-3 týdny)

### REC-AAOS-14: Qdrant + RAG pipeline

```yaml
id: REC-AAOS-14
priority: VYSOKÁ (strategická)
effort: L (2-3 týdny)
gap: GAP-AAOS-002
description: |
  Kompletní RAG infrastruktura:
  1. Qdrant přidat do docker-compose.yml
  2. Embedding pipeline: knowledge/ + platform/docs/ → nomic-embed-text → Qdrant
  3. RAG retrieval: user query → vector search → top-k chunks
  4. BLUEPRINT_SYSTEM_PROMPT augmentace relevantními chunks
implementation_phases:
  phase_1: "Qdrant v docker-compose.yml + indexing script (knowledge/)"
  phase_2: "RAG retrieval API (POST /ai/search-knowledge)"
  phase_3: "BLUEPRINT_SYSTEM_PROMPT augmentace"
health_impact: "+20% Knowledge Engine, +10% Context Engine, +5% Agent Communication"
prerequisite: "Ollama s nomic-embed-text (nebo Anthropic embedding API)"
```

### REC-AAOS-15: Intelligent Provider Router

```yaml
id: REC-AAOS-15
priority: STŘEDNÍ (strategická)
effort: L (1-2 týdny)
gap: GAP-AAOS-004
description: |
  IntelligentRouter třída s capability matrix:
  - context_size: long (>50k tokens) → Anthropic
  - offline: true → Ollama
  - cost_priority: low → Ollama (local)
  - fallback: Anthropic fail → OpenAI-compat
implementation:
  - "packages/ai/router.py: IntelligentRouter"
  - "packages/ai/capability_matrix.py: per-model capabilities"
  - "packages/ai/generator.py: použít IntelligentRouter místo _build_provider()"
health_impact: "+20% Provider Routing"
prerequisite: "Alespoň jeden OpenAI-compat server (Ollama)"
```

### REC-AAOS-16: DIGITAL_TWIN auto-updater

```yaml
id: REC-AAOS-16
priority: STŘEDNÍ
effort: L (1 týden)
gap: GAP-AAOS-015
description: |
  digital_twin_updater.py script:
  - Čte aktuální stav ze všech health score zdrojů
  - Aktualizuje .claude/context/DIGITAL_TWIN.md automaticky
  - Spouštěn: post-commit hook nebo GitHub Actions (weekly-qc.yml)
health_impact: "+5% Self-Optimization, +5% Observability"
```

---

## PRIORITIZOVANÝ SPRINT ROADMAP

```
Sprint 1 (týden 1) — Quick wins, < 8h celkem:
  REC-AAOS-01: max_tokens env var (XS)
  REC-AAOS-02: timeout env var (XS)
  REC-AAOS-03: stub README (XS)
  REC-AAOS-04: RetryConfig napojení (S)
  REC-AAOS-05: AI Prometheus metriky (S)
  → AAOS Health: 38% → 50%

Sprint 2 (týden 2) — Core improvements:
  REC-AAOS-06: 5 knowledge profilů (S)
  REC-AAOS-07: generate-and-run endpoint (S)
  REC-AAOS-08: provider health check (S)
  REC-AAOS-09: Mock providers v CI (M)
  → AAOS Health: 50% → 60%

Sprint 3 (týden 3-4) — Strategic enablers:
  REC-AAOS-10: System prompt parametrizace (M)
  REC-AAOS-11: NATS integrace (M)
  REC-AAOS-12: Scheduled QC (M)
  → AAOS Health: 60% → 68%

Sprint 4 (měsíc 2-3) — Platform maturity:
  REC-AAOS-14: Qdrant + RAG (L)
  REC-AAOS-15: Intelligent Router (L)
  REC-AAOS-16: DIGITAL_TWIN updater (L)
  → AAOS Health: 68% → 80%+
```

**Celkový odhad: 40-80h → AAOS Maturity Level 4 / 5 (health score 80%+)**
