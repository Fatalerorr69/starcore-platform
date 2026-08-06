# KNOWLEDGE REGISTRY

Aktualizováno: 2026-08-06 | Standard: SAKB-000 §17

Centrální registr znalostního systému STARCORE (SAKB). Fyzická data žijí v `knowledge/`, tento registr indexuje jejich stav.

---

## SAKB STRUKTURA

```
knowledge/
├── core/                  ← (existující stub, pre-SAKB, MOD-011)
├── rag/                   ← (existující stub, pre-SAKB, MOD-011)
├── technologies/          ← Technology Profiles (SAKB-000 §6-7)
│   ├── infrastructure/
│   ├── ai/
│   ├── development/
│   └── edge/
├── infrastructure/        ← Infrastructure Knowledge (TYPE 003)
├── ai/                    ← AI Knowledge (TYPE 005)
├── security/              ← Security Knowledge (TYPE 004)
├── operations/             ← Operational Knowledge (TYPE 006)
├── research/               ← Research Pipeline výstupy (SAKB-000 §8)
├── sources/                ← Raw zdrojový materiál (zatím prázdné)
├── packages/                ← Knowledge Packages (SAKB-000 §10)
└── registry/
    └── SOURCE_REGISTRY.md   ← Zdrojový registr (SAKB-000 §5)
```

---

## TECHNOLOGY PROFILES — STAV

| Profil | Kategorie | Soubor | Status |
|---|---|---|---|
| Proxmox VE | Infrastructure | `knowledge/technologies/infrastructure/proxmox-ve.md` | ✅ VYTVOŘEN |
| Docker | Infrastructure | `knowledge/technologies/infrastructure/docker.md` | ✅ VYTVOŘEN |
| Python | Development | `knowledge/technologies/development/python.md` | ✅ VYTVOŘEN |
| FastAPI | Development | `knowledge/technologies/development/fastapi.md` | ✅ VYTVOŘEN |
| Ollama | AI | `knowledge/technologies/ai/ollama.md` | ✅ VYTVOŘEN |
| Anthropic Claude | AI | `knowledge/technologies/ai/anthropic-claude.md` | ✅ VYTVOŘEN |
| Debian | Infrastructure | — | ⏳ PLÁNOVÁNO |
| Ubuntu | Infrastructure | — | ⏳ PLÁNOVÁNO |
| Kubernetes | Infrastructure | — | ⏳ PLÁNOVÁNO |
| Ansible | Infrastructure | — | ⏳ PLÁNOVÁNO |
| Tailscale | Infrastructure | — | ⏳ PLÁNOVÁNO |
| OpenWebUI | AI | — | ⏳ PLÁNOVÁNO |
| Qdrant | AI | — | ⏳ PLÁNOVÁNO |
| Redis | AI | — | ⏳ PLÁNOVÁNO |
| LangChain | AI | — | ⏳ PLÁNOVÁNO |
| MCP | AI | — | ⏳ PLÁNOVÁNO |
| RAG (koncept) | AI | — | ⏳ PLÁNOVÁNO |
| PostgreSQL | Development | — | ⏳ PLÁNOVÁNO |
| GitHub | Development | — | ⏳ PLÁNOVÁNO |
| GitHub Actions | Development | — | ⏳ PLÁNOVÁNO |
| Android | Edge | — | ⏳ PLÁNOVÁNO |
| Termux | Edge | — | ⏳ PLÁNOVÁNO |
| Magisk | Edge | — | ⏳ PLÁNOVÁNO |

**Pokrytí: 6/22 profilů vytvořeno (27 %).** Zbylé profily budou vytvořeny postupně dle Research Pipeline (SAKB-000 §8) při konkrétní implementační potřebě (Fáze 2+ Improvement Roadmap).

---

## KNOWLEDGE PACKAGES

| Package ID | Titul | Kategorie | Soubor | Status |
|---|---|---|---|---|
| PKG-001 | STARCORE AI Provider Abstraction | AI / Architecture | `knowledge/packages/PKG-001-ai-provider-abstraction.md` | ✅ VYTVOŘEN |

---

## ZDROJE

Viz `knowledge/registry/SOURCE_REGISTRY.md` — 9 aktivních zdrojů (vše L5 Official Documentation), 12 plánovaných.

---

## STATISTIKY (Digital Twin Knowledge Status, SAKB-000 §18)

```yaml
sources_registered: 9
sources_planned: 12
technology_profiles_created: 6
technology_profiles_planned: 16
knowledge_packages_created: 1
last_update: 2026-08-06
```

---

## VALIDACE (SAKB-000 §16)

| Kontrola | Poslední běh | Výsledek |
|---|---|---|
| Zastaralé informace | 2026-08-06 | Vše aktuální (nově vytvořeno) |
| Neplatné odkazy | 2026-08-06 | Neověřeno automatizovaně (manuální review) |
| Konflikty verzí | 2026-08-06 | Zaznamenán 1 konflikt: Python 3.11 (systém) vs >=3.12 (platform requirement) — viz `python.md` |
