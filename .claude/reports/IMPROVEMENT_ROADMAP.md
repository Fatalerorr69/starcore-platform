# IMPROVEMENT ROADMAP

Datum: 2026-08-06

---

## FÁZE 1 — KONSOLIDACE A DOKUMENTACE (Týden 1-2)

Cíl: Pochopit a zdokumentovat současný stav.

### Úkoly

| # | Úkol | Priorita | Odhadovaný čas |
|---|---|---|---|
| 1.1 | Vytvořit root `README.md` | KRITICKÁ | 2h |
| 1.2 | Vytvořit `INSTALL_SCRIPTS_REGISTRY.md` | KRITICKÁ | 3h |
| 1.3 | Zmapovat vztahy mezi `platform/` a ostatními vrstvami | VYSOKÁ | 4h |
| 1.4 | Dokumentovat `runtime/` JSON stav soubory | STŘEDNÍ | 2h |
| 1.5 | Vytvořit `.claude/` registries (PROJECT, MODULE, TECH) | STŘEDNÍ | 2h |

---

## FÁZE 2 — DOCKER AI STACK (Týden 2-3)

Cíl: Funkční lokální AI infrastruktura.

### Architektura

```
docker-compose.yml (AI Stack)
├── ollama          ← LLM inference (llama3, mistral, ...)
├── open-webui      ← Chat UI pro Ollama
├── qdrant          ← Vector database (RAG)
├── redis           ← Cache a session store
└── starcore-api    ← STARCORE Platform API
```

### Úkoly

| # | Úkol | Priorita | Odhadovaný čas |
|---|---|---|---|
| 2.1 | Vytvořit `docker/ai-stack/docker-compose.yml` | KRITICKÁ | 3h |
| 2.2 | Konfigurace Ollama s model management | VYSOKÁ | 2h |
| 2.3 | Integrace OpenWebUI → STARCORE API | STŘEDNÍ | 4h |
| 2.4 | Qdrant setup s STARCORE knowledge base | STŘEDNÍ | 3h |
| 2.5 | Dokumentace Docker AI Stack | STŘEDNÍ | 2h |

---

## FÁZE 3 — PROXMOX DEPLOYMENT (Týden 3-4)

Cíl: Reprodukovatelný deployment na Proxmox.

### Architektura

```
Proxmox Host
├── AI Core VM (Ubuntu 24.04)
│   ├── Docker Stack (AI services)
│   └── STARCORE Platform API
├── Database VM (PostgreSQL)
└── Monitoring VM (Grafana + Prometheus)
```

### Úkoly

| # | Úkol | Priorita | Odhadovaný čas |
|---|---|---|---|
| 3.1 | Ansible playbook: AI Core VM setup | VYSOKÁ | 6h |
| 3.2 | Proxmox blueprint: `ai-core-vm.yaml` | VYSOKÁ | 3h |
| 3.3 | PostgreSQL migration (ze SQLite) | STŘEDNÍ | 4h |
| 3.4 | SSL/TLS konfigurace (nginx reverse proxy) | STŘEDNÍ | 3h |
| 3.5 | Backup strategie (Proxmox snapshots + Qdrant) | STŘEDNÍ | 3h |

---

## FÁZE 4 — AGENT FRAMEWORK INTEGRACE (Týden 4-6)

Cíl: Propojit agent vrstvu s Platform API.

### Úkoly

| # | Úkol | Priorita | Odhadovaný čas |
|---|---|---|---|
| 4.1 | Zdokumentovat agent_registry.json strukturu | VYSOKÁ | 2h |
| 4.2 | Propojit agents/ s platform/ Plugin System | VYSOKÁ | 8h |
| 4.3 | AI Agent pro blueprint generaci | STŘEDNÍ | 6h |
| 4.4 | GitHub Actions CI pro agent testy | STŘEDNÍ | 3h |

---

## FÁZE 5 — AUTOMATION A GITHUB INTEGRACE (Průběžně)

### Úkoly

| # | Úkol | Priorita | Odhadovaný čas |
|---|---|---|---|
| 5.1 | GitHub Actions: CD pipeline (auto deploy) | STŘEDNÍ | 4h |
| 5.2 | n8n workflow (nebo GitHub Actions) pro automatizaci | NÍZKÁ | 6h |
| 5.3 | Termux/Android remote access bridge | NÍZKÁ | 8h |

---

## RIZIKA

| Riziko | Pravděpodobnost | Dopad | Mitigace |
|---|---|---|---|
| Install skripty konfliktují | STŘEDNÍ | VYSOKÝ | Zmapovat před spuštěním |
| Proxmox API klíče nedostupné | NÍZKÁ | KRITICKÝ | Připravit bez přístupu |
| SQLite → PostgreSQL migrace selže | NÍZKÁ | VYSOKÝ | Testovat na dev nejprve |
| Ollama VRAM nedostatečná | STŘEDNÍ | STŘEDNÍ | Použít menší modely |

---

## KLÍČOVÉ METRIKY ÚSPĚCHU

- [ ] Docker AI Stack spustitelný jedním příkazem
- [ ] Proxmox deployment reprodukovatelný z nuly
- [ ] Všechny install skripty zdokumentovány v registru
- [ ] Root README existuje a je aktuální
- [ ] Agent framework propojen s Platform API
