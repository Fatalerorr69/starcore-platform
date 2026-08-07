# MEMORY ORCHESTRATION

Standard: SPOS-011 §8 | Aktualizováno: 2026-08-07

Mapa existujících memory vrstev STARCORE a jejich vzájemných vztahů.

---

## MEMORY FLOW (existující implementace)

```
SHORT MEMORY (kontext AI session)
  └── Claude Code conversation context
  └── CONTEXT_RESTORATION_PROTOCOL.md (6-step cold-start)
  ↓

WORKING MEMORY (aktuální session state)
  └── platform/.starcore/sessions/current.md
  └── platform/.starcore/sessions/ledger.yaml (ACTIVE session)
  ↓

LONG MEMORY (persistentní projekt state)
  └── platform/.starcore/memory/current_state.md
  └── platform/.starcore/state/project_state.json
  └── platform/.starcore/memory/project_snapshot.md (ZASTARALÉ — v0.4.0)
  ↓

KNOWLEDGE BASE (strukturovaná znalost)
  └── knowledge/ (6 tech profiles, PKG-001)
  └── .claude/sakb/ (SAKB-000 knowledge model)
  └── .claude/registry/*.md (10+ registrů)
  ↓

ARCHIVE
  └── platform/.starcore/sessions/archive/*.md (uzavřené session handovery)
  └── git history (change memory)
  ↓

SNAPSHOTS
  └── platform/.starcore/reports/ (QC reporty)
  └── .claude/reports/ (SPOS implementation reporty)
  └── .claude/context/DIGITAL_TWIN.md (živý systém snapshot)
```

---

## DETAILNÍ MAPA VRSTEV

### SHORT MEMORY — AI Context

```yaml
layer: SHORT
owner: Claude Code runtime
content:
  - "Aktuální konverzační kontext"
  - "Tool outputs z aktuální session"
persistence: "Do konce konverzace (nebo do komprese)"
restoration: "CONTEXT_RESTORATION_PROTOCOL.md (6 kroků)"
```

### WORKING MEMORY — Session State

```yaml
layer: WORKING
owner: platform/.starcore/sessions/
files:
  - "sessions/current.md — lidsky čitelný aktuální stav"
  - "sessions/ledger.yaml — strojově čitelný YAML (ledger.py)"
cli: "ledger.py start/end/current/add-decision/add-risk/add-file"
persistence: "Do ledger.py end → archivace"
```

### LONG MEMORY — Project State

```yaml
layer: LONG
owner: platform/.starcore/memory/
files:
  - "memory/current_state.md — pointer na aktuální fázi (SPOS-001 addition)"
  - "state/project_state.json — strojově čitelný PROJECT_STATE (SPOS-001 addition)"
  - "memory/project_snapshot.md — ZASTARALÝ (v0.4.0, realita v0.6.0)"
persistence: "Trvale (ruční aktualizace)"
```

### KNOWLEDGE BASE

```yaml
layer: KNOWLEDGE
files:
  - "knowledge/technologies/ (6 tech profiles: proxmox-ve, docker, python, fastapi, ollama, anthropic-claude)"
  - "knowledge/packages/PKG-001-ai-provider-abstraction.md"
  - "knowledge/registry/SOURCE_REGISTRY.md (9 L5 zdrojů)"
  - ".claude/sakb/SAKB-000-KNOWLEDGE-MODEL.md"
status: ČÁSTEČNÉ (6/22 tech profiles vytvořeny)
vector_indexing: CHYBÍ (Qdrant plánován, neexistuje)
```

### ARCHIVE

```yaml
layer: ARCHIVE
files:
  - "platform/.starcore/sessions/archive/2026-07-26-starcore-autonomous-engineering-4p3tlj.md"
  - "git log (change memory — ADR-001..017)"
persistence: "Trvalá"
```

### SNAPSHOTS

```yaml
layer: SNAPSHOTS
files:
  - ".claude/context/DIGITAL_TWIN.md (systém snapshot, aktualizovaný po každém SPOS)"
  - ".claude/reports/FIRST_FULL_AUDIT_REPORT.md (AR-2026-08-06-001)"
  - "platform/reports/*.json (QC výsledky)"
persistence: "Trvalá (git-tracked)"
```

---

## MEZERY

```yaml
missing:
  - "Vector embeddings / RAG: žádná embedding infrastruktura (Qdrant PLANNED)"
  - "Automatická synchronizace memory vrstev: ruční aktualizace"
  - "project_snapshot.md zastaralý (v0.4.0 vs realita v0.6.0) — neopraveno"
  - "Sdílená paměť mezi AI sessions: každá session začíná cold-start"
  - "Memory versioning: žádný diff history pro memory soubory (kromě git)"
```
