# STARCORE AI Platform

**AI-Powered Infrastructure Operating Platform**

---

## Co je STARCORE?

STARCORE je unifikovaná AI infrastrukturní platforma pro správu, automatizaci a provoz self-hosted prostředí. Umožňuje deklarativně popisovat infrastrukturu a nechat STARCORE plánovat a provádět potřebné akce.

---

## Struktura Repository

```
starcore-platform/
├── platform/           ← HLAVNÍ PLATFORMA (Python, v0.6.0)
│   ├── packages/       ← Core logika (AI, blueprints, providers)
│   ├── apps/cli/       ← Typer CLI
│   ├── tests/          ← 601 testů
│   └── docs/           ← Kompletní dokumentace
│
├── agents/             ← Agent framework
├── runtime/            ← Runtime state
├── knowledge/          ← Knowledge base (RAG)
├── security/           ← Bezpečnostní vrstva
├── intelligence/       ← Intelligence layer
├── ai_core/            ← AI core
├── automation/         ← Automation
│
├── install_*.sh        ← Instalační skripty (64 skriptů)
└── .claude/            ← AI Engineering context
```

---

## Rychlý start

### Platform (Python)

```bash
cd platform/
uv sync --extra dev
cp .env.example .env
uv run starcore blueprint plan packages/blueprints/examples/basic.yaml
```

### Více informací

- [Platform README](platform/README.md) — detailní popis platformy
- [Architektura](.claude/reports/CURRENT_ARCHITECTURE.md)
- [Roadmap](.claude/reports/IMPROVEMENT_ROADMAP.md)
- [AI Engineering Reports](.claude/reports/)

---

## Cílová infrastruktura

```
Local PC → GitHub → Proxmox → VM/LXC → Docker → AI Services → Agents
```

**AI Stack:** Ollama + OpenWebUI + Qdrant + Redis + STARCORE API

---

## Licence

Apache-2.0 — viz [platform/LICENSE](platform/LICENSE)
