# KNOWLEDGE ORCHESTRATION

Standard: SPOS-011 §9 | Aktualizováno: 2026-08-07

Mapa knowledge systému STARCORE a plán pro RAG orchestraci.

---

## EXISTUJÍCÍ KNOWLEDGE INFRASTRUKTURA

### knowledge/ adresář (ověřeno v SAKB-000)

```yaml
location: knowledge/
structure:
  technologies/:
    ai/:
      - anthropic-claude.md ✅
      - ollama.md ✅
    development/:
      - python.md ✅
      - fastapi.md ✅
    infrastructure/:
      - proxmox-ve.md ✅
      - docker.md ✅
    edge/:
      - (prázdné — plánováno)
  packages/:
    - PKG-001-ai-provider-abstraction.md ✅
  registry/:
    - SOURCE_REGISTRY.md (9 L5 zdrojů) ✅
  rag/:      # adresář existuje, prázdný
  research/: # adresář existuje, prázdný

total_profiles: 6 vytvořeny / 22 plánováno
knowledge_packages: 1
sources: 9 (všechny L5 — Official Documentation)
```

### .claude/sakb/

```yaml
location: .claude/sakb/
files:
  - SAKB-000-KNOWLEDGE-MODEL.md ✅
role: "Governance model pro knowledge base — definuje formáty, procesy"
```

### platform/docs/

```yaml
location: platform/docs/
files: 56 Markdown dokumentů
format: MkDocs (mkdocs.yml)
build: mkdocs build --strict → PASS ✅
categories:
  - ADR (17 dokumentů) ✅
  - Architecture ✅
  - API ✅
  - Security ✅
  - Testing ✅
  - Operations ✅
```

---

## RAG PLÁN (neimplementováno)

```yaml
planned_rag_pipeline:
  step_1_indexing:
    source: "knowledge/ + platform/docs/ + .claude/context/*.md"
    chunking: "Markdown heading-based (H2/H3)"
    embedding_model: "PLÁNOVANÝ (např. nomic-embed-text přes Ollama)"
    vector_db: "Qdrant (PLÁNOVANÝ — není v docker-compose.yml)"
    status: CHYBÍ

  step_2_retrieval:
    query: "Přirozený jazyk dotaz od AI agenta"
    top_k: 5
    threshold: 0.7
    reranker: "Volitelné"
    status: CHYBÍ

  step_3_augmentation:
    inject_context: "Relevantní chunks vloženy do AI systémového promptu"
    provider: "Anthropic nebo OpenAI-compat"
    status: CHYBÍ

estimated_effort: "VYSOKÝ — vyžaduje Qdrant nasazení, embedding pipeline"
prerequisite: "ai-core VM s Ollama + Qdrant"
```

---

## KNOWLEDGE GOVERNANCE (SAKB-000)

```yaml
update_process:
  - "Nové technologie → Technology Profile (knowledge/technologies/)"
  - "Nové packages → Knowledge Package (knowledge/packages/)"
  - "Nové zdroje → SOURCE_REGISTRY.md"
  - "Vše musí být L5 (Official Documentation) nebo výše"

quality_levels:
  L1: Anekdotické (blogposty)
  L2: Komunitní (Stack Overflow)
  L3: Peer-reviewed
  L4: Vendor documentation
  L5: Official Documentation (všechny aktuální zdroje jsou L5)

missing_profiles:
  - "edge/, kubernetes/, ansible/, terraform/, redis/, postgresql/, nats/, prometheus, grafana, ..."
  - "16 zbývajících z 22 plánovaných"
```

---

## ADR JAKO KNOWLEDGE SOURCE

```yaml
adr_count: 17 (ADR-001..017)
location: platform/docs/adr/
role: "Archivovaná rozhodnutí — klíčový knowledge zdroj pro AI kontext"
key_adrs_for_ai:
  - ADR-008: Security Architecture
  - ADR-010: Task execution (depends_on = success gate)
  - ADR-011: Plugin sandbox
  - ADR-012: Single API key model
  - ADR-013+: Pozdější rozhodnutí (neprošel jsem všechny v SPOS sekvenci)
```
