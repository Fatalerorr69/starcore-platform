# SAKB-000 — STARCORE AI KNOWLEDGE BASE MODEL

```yaml
Document ID:     SAKB-000
Title:           STARCORE AI Knowledge Base Model
Version:         1.0.0
Status:          ACTIVE — APPROVED
Parent:          SES-000 (Constitution), SES-001 (Technical Standard)
Repository:      Fatalerorr69/starcore-platform
Branch:          claude/starcore-ai-bootstrap-fkyb96
Date Created:    2026-08-06
```

SES definuje pravidla. SAKB definuje jak STARCORE získává, ukládá, validuje, aktualizuje a používá znalosti pro AI workflow.

---

## 1. PURPOSE

Centrální znalostní vrstva projektu. Cíl: shromažďovat, analyzovat, dokumentovat a poskytovat kontext pro AI rozhodování.

## 2. KNOWLEDGE ARCHITECTURE

```
SOURCE → COLLECTION → VALIDATION → KNOWLEDGE PACKAGE → REGISTRY → AI CONTEXT → IMPLEMENTATION
```

## 3. KNOWLEDGE TYPES

| Typ | Obsah | Umístění |
|---|---|---|
| TYPE 001 Project Knowledge | Architektura, rozhodnutí, roadmapa | `.claude/reports/`, `.claude/context/` |
| TYPE 002 Technology Knowledge | Proxmox, Docker, Python, Claude, Ollama, ... | `knowledge/technologies/` |
| TYPE 003 Infrastructure Knowledge | Servery, VM, sítě, storage | `knowledge/infrastructure/` |
| TYPE 004 Security Knowledge | Hardening, CVE, audity | `knowledge/security/` |
| TYPE 005 AI Knowledge | Modely, agenti, RAG, MCP | `knowledge/ai/` |
| TYPE 006 Operational Knowledge | Instalace, troubleshooting, runbooky | `knowledge/operations/` |

## 4. REPOSITORY MODEL — IMPLEMENTOVÁNO

```
knowledge/
├── core/, rag/          ← pre-existující stub moduly (MOD-011)
├── technologies/{infrastructure,ai,development,edge}/
├── infrastructure/
├── ai/
├── security/
├── operations/
├── research/
├── sources/
├── packages/
└── registry/SOURCE_REGISTRY.md
```

## 5-10. SOURCE REGISTRY, TECHNOLOGY PROFILES, RESEARCH PIPELINE, SOURCE QUALITY, KNOWLEDGE PACKAGE FORMAT

Implementováno dle specifikace — viz `knowledge/registry/SOURCE_REGISTRY.md`, `knowledge/technologies/*`, `knowledge/packages/PKG-001-*.md`.

Trust levels L1-L5 aplikovány; všechny aktuální zdroje jsou L5 (Official Documentation).

## 11. AI CONTEXT MANAGEMENT

AI agent (Claude Code) před prací: načte relevantní Knowledge Package → ověří `last_update` aktuálnost → použije pouze relevantní kontext → po dokončení aktualizuje `KNOWLEDGE_REGISTRY.md` a `DIGITAL_TWIN.md`.

## 12-13. AUTOMATIC COLLECTION / GITHUB INTEGRATION

Zatím manuální proces (tento bootstrap). Automatizace (GitHub Actions scanning, release monitoring) je PLÁNOVANÁ — kandidát pro Fázi 5 Improvement Roadmap.

## 14. AI WORKFLOW INTEGRATION

SAKB poskytuje kontext přes Markdown soubory čitelné jakýmkoli AI nástrojem (Claude Code, Codex, Gemini). Strukturovaný YAML uvnitř Markdown umožňuje snadné strojové parsování.

## 15. RAG PREPARATION

Metadata struktura (source, category, version, date, confidence) je v Technology Profiles a Knowledge Packages připravena pro budoucí Qdrant embedding pipeline (MOD-102, zatím neimplementováno).

## 16. KNOWLEDGE VALIDATION

Viz `KNOWLEDGE_REGISTRY.md` validační sekce — 1 zjištěný konflikt (Python verze) zaznamenán.

## 17-18. REGISTRY / DIGITAL TWIN INTEGRATION

`TECHNOLOGY_REGISTRY.md`, `DOCUMENTATION_REGISTRY.md`, `AI_REGISTRY.md` aktualizovány. `KNOWLEDGE_REGISTRY.md` nově vytvořen. `DIGITAL_TWIN.md` rozšířen o Knowledge Status sekci.

---

## STAV IMPLEMENTACE

```yaml
sources: 9 (all L5)
technology_profiles: 6/22 (27%)
knowledge_packages: 1
research_pipeline: defined, not yet automated
rag_preparation: metadata structure ready, embedding pipeline not implemented
```

## NEXT

Čekat na **SPOS-000 — STARCORE Project Operating System Bootstrap**.
