# PROMPT ENGINE

Standard: SPOS-014 §9 | Aktualizováno: 2026-08-07

Dokumentace Prompt Engine STARCORE AAOS — správa, struktura a použití promptů.

---

## PŘEHLED

```yaml
prompt_engine_status: ZÁKLADNÍ (AKTIVNÍ)
central_prompt: BLUEPRINT_SYSTEM_PROMPT (packages/ai/prompts.py)
prompt_registry: platform/.starcore/prompts/registry.yaml (PROM-001..009)
dynamic_prompts: CHYBÍ
rag_augmentation: CHYBÍ
prompt_versioning: CHYBÍ (git history jako záloha)
```

---

## BLUEPRINT_SYSTEM_PROMPT (primární AI prompt)

```yaml
location: "platform/packages/ai/prompts.py"
constant: BLUEPRINT_SYSTEM_PROMPT
type: "System prompt (Anthropic Messages API systémové pole)"
purpose: "Instrukce pro AI generování YAML blueprintů pro infrastrukturní provisioning"
```

### Obsah promptu (ověřeno auditem)

```yaml
blueprint_system_prompt_content:
  resource_types:
    docker:
      - container: "Docker kontejner (image, name, ports, env, volumes, command)"
    proxmox:
      - vm: "Proxmox Virtual Machine"
      - lxc: "Proxmox LXC kontejner"

  depends_on_rules:
    - "depends_on: [] — žádné závislosti"
    - "depends_on: [resource_name] — čeká na SUCCESS jiného resource"
    - "Tranzitivní propagace SKIPPED_DEPENDENCY_FAILED"

  output_format:
    - "Čistý YAML bez Markdown kódových ohraničení"
    - "resources: lista ResourceSpec objektů"
    - "_strip_code_fences() odstraní ```yaml``` wrapper pokud AI přidá"

  resource_naming_conventions:
    - "Lowercase kebab-case (web-server, db-primary)"
    - "Unikátní v rámci blueprintu"
```

### Prompt pipeline

```
User description (přirozený jazyk)
  ↓
BLUEPRINT_SYSTEM_PROMPT (system field)
  ↓
AI Provider (Anthropic nebo OpenAI-compat)
  ↓
Raw text response
  ↓
_strip_code_fences(text)
  ↓
YAML string → BlueprintLoader.load() → Blueprint | validation_error
```

---

## PROMPT REGISTRY (platform/.starcore/prompts/registry.yaml)

Spravováno přes `python .starcore/scripts/registry.py`:

```yaml
registry_location: "platform/.starcore/prompts/registry.yaml"
cli: "python .starcore/scripts/registry.py register|list|get|update|delete"
```

### Registrované prompty (PROM-001..009)

| ID | Název | Typ | Status |
|---|---|---|---|
| PROM-001 | CONTEXT_RESTORATION_PROTOCOL | Governance | AKTIVNÍ |
| PROM-002 | SPOS Engineering Standard | Governance | AKTIVNÍ |
| PROM-003 | Decision Engine Protocol | Governance | AKTIVNÍ |
| PROM-004 | Blueprint Generation | Platform AI | AKTIVNÍ |
| PROM-005 | QC Engine Protocol | Governance | AKTIVNÍ |
| PROM-006 | Security Review Protocol | Governance | AKTIVNÍ |
| PROM-007 | Impact Analysis Protocol | Governance | AKTIVNÍ |
| PROM-008 | Session Management Protocol | Governance | AKTIVNÍ |
| PROM-009 | SPOS-013 Automation Engine | SPOS Standard | AKTIVNÍ |

---

## PROMPT ARCHITEKTURA

```
┌─────────────────────────────────────────────────────┐
│                 PROMPT ENGINE                        │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Platform AI Prompt                          │    │
│  │  BLUEPRINT_SYSTEM_PROMPT (packages/ai/)  ✅  │    │
│  │  • Resource type definitions                 │    │
│  │  • Dependency rules                          │    │
│  │  • Output format constraints                 │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Governance Prompts                          │    │
│  │  Prompt Registry (registry.yaml)         ✅  │    │
│  │  PROM-001..009 (9 registrovaných)            │    │
│  │  CLI: registry.py register|list             │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Dynamic Prompt Augmentation             ❌  │    │
│  │  (RAG context injection — PLÁNOVÁNO)         │    │
│  │  • Qdrant vector retrieval                   │    │
│  │  • Relevantní knowledge chunks               │    │
│  └─────────────────────────────────────────────┘    │
│                                                      │
│  ┌─────────────────────────────────────────────┐    │
│  │  Prompt Versioning                       ❌  │    │
│  │  (git history jako záloha, ne formální)      │    │
│  │  • Žádný A/B testing                         │    │
│  │  • Žádné prompt metrics (quality tracking)   │    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## PROMPT POUŽITÍ PER AGENT

| Agent | System Prompt | User Message | Typ |
|---|---|---|---|
| AGENT-001 | BLUEPRINT_SYSTEM_PROMPT | description (přirozený jazyk) | AI inference |
| AGENT-002 | N/A | N/A | Programatický (asyncio) |
| AGENT-003 | PROM-005 (QC protocol) | N/A | Governance CLI |
| AGENT-004 | PROM-007 (Impact Analysis) | N/A | Governance CLI |
| Claude Code (tento agent) | SPOS-0XX prompt | Uživatelské zprávy | AI engineering agent |

---

## PROMPT ENGINE GAPS

```yaml
prompt_gaps:
  GAP-PE01:
    description: "BLUEPRINT_SYSTEM_PROMPT je statická konstanta"
    impact: "Nelze přizpůsobit pro různé use cases bez změny kódu"
    solutions:
      - "Parametrizace přes Settings (STARCORE_BLUEPRINT_PROMPT_EXTRA)"
      - "RAG augmentace (runtime knowledge injection)"
    priority: MEDIUM

  GAP-PE02:
    description: "Žádné prompt versioning nebo A/B testing"
    impact: "Nelze měřit kvalitu generovaných blueprintů přes čas"
    priority: LOW

  GAP-PE03:
    description: "9 governance promptů bez automatické aplikace"
    impact: "Prompty jsou dokumenty, ne runtime instrukce"
    current: "PROM-001..009 jsou referenční dokumentace pro Claude Code sessions"
    priority: LOW

  GAP-PE04:
    description: "max_tokens=2000 hardcoded pro AnthropicProvider"
    impact: "Složité blueprinty (mnoho resources) mohou být oříznuty"
    location: "packages/ai/providers/anthropic.py"
    solution: "STARCORE_AI_MAX_TOKENS env var"
    priority: MEDIUM
```

---

## PLÁNOVANÝ PROMPT ENGINE

```yaml
planned_features:
  PE-P01:
    name: "Prompt Template System"
    description: "Jinja2 templates pro BLUEPRINT_SYSTEM_PROMPT + knowledge injection"
    effort: LOW

  PE-P02:
    name: "RAG Augmentation"
    description: "Automatická injekce relevantních knowledge chunks do system promptu"
    prerequisite: "Qdrant + nomic-embed-text (Ollama)"
    effort: HIGH

  PE-P03:
    name: "Prompt Quality Metrics"
    description: "Tracking: blueprint validation rate, parse errors, retry count"
    effort: MEDIUM
    integration: "EventBus + Prometheus metrics"

  PE-P04:
    name: "Dynamic max_tokens"
    description: "STARCORE_AI_MAX_TOKENS env var pro AnthropicProvider"
    effort: XS (< 30 min)
```
