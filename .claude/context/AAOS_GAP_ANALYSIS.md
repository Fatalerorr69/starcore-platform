# AAOS GAP ANALYSIS

Standard: SPOS-014 §11 | Aktualizováno: 2026-08-07

Kompletní gap analýza AI Agent Operating System vrstvy. Vychází z SPOS-014 discovery.

---

## PŘEHLED

```yaml
total_gaps: 22
critical: 5
high: 8
medium: 6
low: 3
aaos_health_impact: "-62% (od ideálního 100% k aktuálním 38%)"
```

---

## KRITICKÉ GAPY (5) — Blokují AAOS Level 3+

### GAP-AAOS-001: Nulová multi-agent koordinace

```yaml
id: GAP-AAOS-001
severity: KRITICKÝ
title: "Multi-agent komunikace neexistuje"
description: |
  4 reálné agenty (AGENT-001..004) fungují v absolutní izolaci.
  Žádný cross-agent messaging, žádný sdílený kontext, žádný orchestrátor.
  EventBus existuje ale pouze pro task events (task.started/completed/run.completed),
  ne pro agent-to-agent komunikaci.
affected_agents: [AGENT-001, AGENT-002, AGENT-003, AGENT-004]
root_cause: "NATS (docker-compose scaffold) neintegrován do aplikační logiky"
impact:
  - "Nelze implementovat komplexní AI workflow (blueprint gen → auto run)"
  - "QC výsledky nelze automaticky předat CI/CD pipeline"
  - "AAOS zůstává Level 2 bez tohoto gapu"
remediation: "GAP-AAOS-001 → REC-AAOS-01 (NATS integrace)"
aaos_health_loss: "-30% na Agent Communication dimenzi"
```

### GAP-AAOS-002: RAG pipeline neexistuje

```yaml
id: GAP-AAOS-002
severity: KRITICKÝ
title: "Žádný vector store ani RAG pipeline"
description: |
  knowledge/rag/rag_engine.py je 7-řádkový JSON print stub.
  Qdrant zmíněn v SPOS-011 ale není v docker-compose.yml.
  6/22 knowledge profilů vytvořeno — beze znalostního retrieval systému
  AI nemůže využít knowledge base v runtime.
root_cause: "Qdrant (vector DB) neexistuje v infrastruktuře"
impact:
  - "BLUEPRINT_SYSTEM_PROMPT nemůže být augmentován knowledge chunky"
  - "AI agenti nemají přístup k project knowledge v runtime"
  - "Knowledge Engine health: 30% (místo 80%+ s RAG)"
remediation: "GAP-AAOS-002 → REC-AAOS-02 (Qdrant + embedding pipeline)"
aaos_health_loss: "-20% na Knowledge Engine dimenzi"
```

### GAP-AAOS-003: Infra providers offline — blueprint execution DEGRADED

```yaml
id: GAP-AAOS-003
severity: KRITICKÝ
title: "3/3 infra providers offline"
description: |
  DockerProvider, ProxmoxProvider, KubernetesProvider jsou všechny OFFLINE.
  Blueprint execution kód je kompletní a testovaný ale nemůže provést
  žádný reálný infrastructure task.
  Identifikováno v SPOS-013 (GAP-002), pokračuje v SPOS-014.
root_cause: "Chybí: Docker daemon, Proxmox credentials, Kubernetes cluster"
impact:
  - "AAOS Workflow Orchestration: 55% (místo 85%+ s providers)"
  - "Žádné end-to-end blueprint testing v CI"
  - "AGENT-002 je funkční ale nepoužitelný na produkčních workloadech"
remediation: "GAP-AAOS-003 → REC-AAOS-03 (Mock providers v CI)"
aaos_health_loss: "-25% na Workflow Orchestration dimenzi"
```

### GAP-AAOS-004: Žádný runtime Provider Router

```yaml
id: GAP-AAOS-004
severity: KRITICKÝ
title: "Provider routing je statický env-var, žádná runtime intelligence"
description: |
  _build_provider(settings) — jednoduchý if/else na STARCORE_AI_PROVIDER.
  Žádná health check před voláním, žádný fallback, žádná cost optimization.
  Při selhání Anthropic API → BlueprintGenerationError bez retry.
impact:
  - "Systém se nepřepne na OpenAI-compat při výpadku Anthropic"
  - "Žádná cost optimization (vždy cloud API, nikdy local Ollama)"
  - "Provider Routing: 40% (místo 80%+ s intelligent router)"
remediation: "GAP-AAOS-004 → REC-AAOS-04 (Intelligent Provider Router)"
aaos_health_loss: "-20% na Provider Routing dimenzi"
```

### GAP-AAOS-005: 21+ stub agentů bez implementace

```yaml
id: GAP-AAOS-005
severity: KRITICKÝ
title: "agents/, autonomous/, distributed/ jsou JSON print stubs"
description: |
  21+ Python souborů v agents/, autonomous/, distributed/, ai_runtime/ a knowledge/
  vypadají jako reálné AI komponenty ale jsou Termux stubs (~16 řádků každý).
  Zapisují JSON do ~/STARCORE/ path (homelab Android path) — nepoužitelné v platform/.
  Uživatelé nebo AI mohou být uvedeni v omyl o rozsahu implementace.
impact:
  - "Agent Coverage: 35% (4 reálné / 4+21 = 81 celkem)"
  - "False impression of mature AI system"
remediation: "GAP-AAOS-005 → REC-AAOS-05 (Dokumentovat stubs, nebo implementovat/smazat)"
aaos_health_loss: "-25% na Agent Coverage dimenzi"
```

---

## VYSOKÉ GAPY (8) — Omezují AAOS efektivitu

### GAP-AAOS-006: Plugin system bez sandboxingu

```yaml
id: GAP-AAOS-006
severity: VYSOKÝ
title: "Pluginy mají plný process přístup (ADR-011 known)"
description: |
  importlib.import_module() spustí plugin kód s plnými právy STARCORE procesu
  dříve než register() je zavolán. Known limitation (ADR-011).
  Pokud se přidá malicious plugin (nebo kompromitovaný), má přístup ke všemu.
impact:
  - "Security/Sandboxing: 45% (místo 70%+ se sandboxingem)"
  - "2 aktivní pluginy: example_provider, run_logger"
  - "STARCORE_PLUGINS_ALLOWLIST existuje ale nenahrazuje sandbox"
priority: VYSOKÝ (known risk, documented)
```

### GAP-AAOS-007: Žádné AI inference observability

```yaml
id: GAP-AAOS-007
severity: VYSOKÝ
title: "Chybí metriky pro AI calls (latency, token count, cost, error rate)"
description: |
  Prometheus má BLUEPRINT_TASKS_TOTAL ale žádné AI-specific metriky.
  Nelze měřit: AI call latency per provider, token consumption, blueprint
  generation success rate, validation error rate.
impact:
  - "Observability: 50% (AI část: 0%)"
  - "Nelze detekovat AI provider degradaci"
  - "Nelze optimalizovat prompty bez dat"
```

### GAP-AAOS-008: max_tokens=2000 hardcoded

```yaml
id: GAP-AAOS-008
severity: VYSOKÝ
title: "AnthropicProvider má max_tokens=2000 jako hardcoded konstanta"
description: |
  packages/ai/providers/anthropic.py: max_tokens=2000
  Složité blueprinty s mnoha resources (5+) mohou být oříznuty.
  Žádná env var pro konfiguraci.
effort: XS (< 30 min fix)
```

### GAP-AAOS-009: RetryConfig nenapojeno na AI providers

```yaml
id: GAP-AAOS-009
severity: VYSOKÝ
title: "RetryConfig existuje v provider_sdk ale AI providers ho nepoužívají"
description: |
  packages/provider_sdk/retry.py: RetryConfig + attempt_with_retry implementováno.
  AnthropicProvider a OpenAICompatProvider nemají žádný retry mechanismus.
  API rate limits (429) způsobí okamžitý BlueprintGenerationError.
effort: S (1-2h)
```

### GAP-AAOS-010: Knowledge base neúplná (6/22 profilů)

```yaml
id: GAP-AAOS-010
severity: VYSOKÝ
title: "Pouze 6/22 technology profilů vytvořeno"
description: |
  Existuje: proxmox-ve, docker, python, fastapi, anthropic-claude, ollama.
  Chybí: redis, postgresql, nats, kubernetes, prometheus, grafana, ansible,
  terraform, nginx, lxc, zfs, pve-firewall, ...
  knowledge/ai/ adresář je prázdný.
```

### GAP-AAOS-011: BLUEPRINT_SYSTEM_PROMPT statický

```yaml
id: GAP-AAOS-011
severity: VYSOKÝ
title: "System prompt nelze parametrizovat ani augmentovat za runtime"
description: |
  Konstanta v packages/ai/prompts.py — žádná Jinja2 parametrizace,
  žádná knowledge injection, žádný per-request customization.
  Všechny blueprinty generovány se stejným kontextem bez ohledu na
  dostupné infrastrukturní resources.
```

### GAP-AAOS-012: Žádný agent health monitoring

```yaml
id: GAP-AAOS-012
severity: VYSOKÝ
title: "Žádná automatická detekce degradace agentů"
description: |
  GET /providers/{name}/health funguje manuálně pro infra providers.
  Žádný health check pro AI providers (je Anthropic API dostupná?).
  Žádný periodic health loop pro agenty.
```

### GAP-AAOS-013: EventBus bez perzistence

```yaml
id: GAP-AAOS-013
severity: VYSOKÝ
title: "EventBus je in-memory — zprávy ztraceny při restartu"
description: |
  packages/core/events.py: čistě in-process asyncio pub/sub.
  Při restartu STARCORE serveru jsou ztraceny všechny in-flight events.
  NATS v docker-compose.yml ale EventBus ho nepoužívá.
```

---

## STŘEDNÍ GAPY (6)

| ID | Popis | Priorita |
|---|---|---|
| GAP-AAOS-014 | Žádná agent permission model (všichni agenti mají stejná práva) | STŘEDNÍ |
| GAP-AAOS-015 | DIGITAL_TWIN bez auto-sync (ruční aktualizace po každém SPOS) | STŘEDNÍ |
| GAP-AAOS-016 | project_snapshot.md zastaralý (v0.4.0 vs v0.6.0) | STŘEDNÍ |
| GAP-AAOS-017 | Žádné AI output sanitization / content filtering | STŘEDNÍ |
| GAP-AAOS-018 | OpenAI-compat provider timeout 120s hardcoded | STŘEDNÍ |
| GAP-AAOS-019 | Žádná agent versioning (nelze provozovat více verzí agenta) | STŘEDNÍ |

---

## NÍZKÉ GAPY (3)

| ID | Popis | Priorita |
|---|---|---|
| GAP-AAOS-020 | knowledge/ai/ adresář prázdný (plánováno, nevytvořeno) | NÍZKÁ |
| GAP-AAOS-021 | Prompt Registry (PROM-001..009) bez automatické aplikace | NÍZKÁ |
| GAP-AAOS-022 | Žádný A/B testing pro BLUEPRINT_SYSTEM_PROMPT varianty | NÍZKÁ |

---

## GAP COVERAGE MATRIX

| AAOS Komponenta | Kritické gapy | Vysoké gapy | Celkem | Health dopad |
|---|---|---|---|---|
| Multi-Agent Layer | GAP-001 | GAP-013 | 2 | -30% |
| Knowledge Engine | GAP-002, GAP-010 | — | 2 | -20% |
| Infra Providers | GAP-003 | — | 1 | -25% |
| Provider Router | GAP-004 | GAP-009, GAP-018 | 3 | -20% |
| Agent Coverage | GAP-005 | GAP-012, GAP-014 | 3 | -25% |
| Security | — | GAP-006, GAP-017 | 2 | -15% |
| Observability | — | GAP-007 | 1 | -20% |
| Prompt Engine | — | GAP-008, GAP-011 | 2 | -15% |
| Memory/Context | — | GAP-015, GAP-016 | 2 | -10% |

---

## IMPLEMENTAČNÍ ROADMAP

```yaml
sprint_1_critical:
  title: "Quick wins (< 1 týden)"
  items:
    - "REC-AAOS-06: max_tokens env var (XS)"
    - "REC-AAOS-07: RetryConfig napojit na AI providers (S)"
    - "REC-AAOS-08: AI inference metrics (S)"
    - "REC-AAOS-09: Doplnit 5 knowledge profilů (S)"

sprint_2_high:
  title: "Střední (2-4 týdny)"
  items:
    - "REC-AAOS-03: Mock providers v CI (M)"
    - "REC-AAOS-05: Stub cleanup / dokumentace (S)"
    - "REC-AAOS-10: BLUEPRINT_SYSTEM_PROMPT parametrizace (S)"

sprint_3_strategic:
  title: "Strategické (1-3 měsíce)"
  items:
    - "REC-AAOS-01: NATS integrace multi-agent (L)"
    - "REC-AAOS-02: Qdrant + RAG pipeline (L)"
    - "REC-AAOS-04: Intelligent Provider Router (M)"
```
