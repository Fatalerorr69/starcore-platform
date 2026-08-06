# INFRASTRUCTURE MAP

Standard: SPOS-007 §3, §18 | Aktualizováno: 2026-08-06

---

## INFRASTRUCTURE MODEL (§3)

```
DATACENTER (uživatelův homelab — lokace neznámá)
  │
  └─ HOST-002: Proxmox Host (NEDOSTUPNÝ z tohoto prostředí)
       │
       └─ HYPERVISOR: Proxmox VE
            │
            ├─ VM-101 ai-core        [PLÁNOVÁNO] → SERVICE: ollama, open-webui, qdrant, redis, starcore-api
            ├─ VM-102 database       [PLÁNOVÁNO] → SERVICE: postgresql
            └─ VM-103 monitoring     [PLÁNOVÁNO] → SERVICE: prometheus, grafana

HOST-001: Claude Code Remote Container (AKTIVNÍ, toto prostředí)
  │
  └─ SERVICE: platform/ (STARCORE Platform kód, testy, CI toolchain)
       └─ APPLICATION: FastAPI + Typer CLI (spustitelné lokálně, docker-compose definován ale
                        Docker daemon zde neběží)

HOST-003: Android Edge Node (PŘIPRAVENO, NEDOSTUPNÉ)
  │
  └─ Termux + OSIRIS + STARCORE Edge Agent [instalační skripty existují, nespuštěno]
```

---

## REGISTRY INDEX (§18 výstupy)

| Registr | Soubor | Obsah |
|---|---|---|
| Hardware | `.claude/registry/HARDWARE_REGISTRY.md` | 3 hosty (1 aktivní, 2 plánované) |
| Compute (VM/LXC) | `.claude/registry/COMPUTE_REGISTRY.md` | 3 plánované VM, 0 reálných |
| Containers | `.claude/registry/CONTAINER_REGISTRY.md` | 4 definované služby, 0 běžících (Docker daemon nedostupný) |
| Remote Services | `.claude/registry/REMOTE_SERVICE_REGISTRY.md` | 4 služby (GitHub, Anthropic aktivní; Proxmox nedostupný; Ollama plánováno) |

Předchůdce (Bootstrap 00): `.claude/registry/INFRASTRUCTURE_REGISTRY.md` — nyní **rozdělen** do specializovaných registrů výše dle SPOS-007 §18. Zůstává jako obecný přehled, nekonfliktní.

---

## §8 AI INFRASTRUCTURE MAP

| Komponenta | Status |
|---|---|
| LLM (Ollama) | PLÁNOVÁNO |
| Vector DB (Qdrant) | PLÁNOVÁNO |
| Agents (agents/kernel) | AKTIVNÍ, nedokumentováno (MOD-010 gap) |
| APIs (Anthropic Claude) | AKTIVNÍ |
| Automation (AI Blueprint Generation) | AKTIVNÍ (volitelné, vyžaduje API klíč) |
| OpenWebUI, ComfyUI, Whisper, Piper | NEZMÍNĚNO nikde v kódu — mimo aktuální scope, PLÁNOVÁNO jen OpenWebUI (viz IMPROVEMENT_ROADMAP) |

## §9 ANDROID EDGE NODE

Model `EDGE NODE → API → CONTROL PLANE` — v kódu existují pouze instalační skripty (`install_TERMUX_*.sh`, 10 souborů), žádná live registrace edge node vůči control plane. STATUS: PŘIPRAVENO, NEIMPLEMENTOVÁNO.

## §11 NETWORK ARCHITECTURE

| Prvek | Status |
|---|---|
| LAN | NEZNÁMÉ (mimo dosah) |
| VPN/Tailscale | Zmíněno jako Technology Profile kandidát (SAKB-000), neimplementováno |
| SSH | Dostupné v tomto prostředí (agent proxy), ne k Proxmox |
| Reverse Proxy | NEEXISTUJE |
| API Gateway | `platform/api_gateway/` adresář existuje v root repo — **nedokumentováno, vyžaduje audit** (nový nález) |

## §12 SECURITY MODEL (odkaz)

Viz `.claude/reports/FIRST_FULL_AUDIT_REPORT.md` (A03 Security Audit) a `platform/SECURITY.md`. Secrets: žádné nalezeny v `.claude/` ani `knowledge/` (dodrženo SES-000 P007).

## §14 MONITORING

| Nástroj | Status |
|---|---|
| Prometheus | Integrováno v platformě (`GET /metrics`), VM-103 plánováno pro dedikovaný monitoring stack |
| Grafana | PLÁNOVÁNO (VM-103) |
| Logs | Loguru (structured, `STARCORE_LOG_JSON`) — AKTIVNÍ |
| Alerts | NEEXISTUJÍ |

## §15 BACKUP & RECOVERY

| Prvek | Status |
|---|---|
| Proxmox snapshoty | Implementováno v kódu (`starcore snapshot create/list/delete/rollback`, MOD-006) — funkční, ale netestovatelné bez reálného Proxmoxu |
| Backup policy (obecná) | NEDOKUMENTOVÁNO jako samostatný dokument |
| Disaster recovery | NEDOKUMENTOVÁNO |
| `backups/` adresář (root repo) | Existuje, obsah neaudi­tován — nový nález pro budoucí audit |

---

## NOVÉ NÁLEZY (živě zjištěno při tomto auditu)

1. **`api_gateway/` v root repo** — samostatný adresář, nezmíněn v MODULE_REGISTRY (MOD-010..015), vyžaduje audit
2. **`backups/` v root repo** — obsah neznámý, vyžaduje audit
3. **Docker daemon v tomto prostředí neběží** — oprava dřívějšího Bootstrap 00 tvrzení "Docker: Aktivní" → ve skutečnosti jen CLI binárka
