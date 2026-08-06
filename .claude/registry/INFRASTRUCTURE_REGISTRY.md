# INFRASTRUCTURE REGISTRY

Aktualizováno: 2026-08-06 | Standard: SES-000

---

## AKTUÁLNÍ PROSTŘEDÍ (Claude Code Remote)

| Položka | Hodnota | Status |
|---|---|---|
| Typ | Cloud container (ephemeral) | AKTIVNÍ |
| OS | Linux 6.18.5-fc-v18 x86\_64 | AKTIVNÍ |
| CPU | Intel Xeon @ 2.80GHz | AKTIVNÍ |
| RAM | 15 GiB | AKTIVNÍ |
| Disk | 252 GB (7.1 GB použito) | AKTIVNÍ |
| Docker | 29.3.1 | AKTIVNÍ |
| Python | 3.11.15 | AKTIVNÍ |
| Node.js | 22.22.2 | AKTIVNÍ |

---

## CÍLOVÁ INFRASTRUKTURA

### Proxmox Host

| Položka | Hodnota | Status |
|---|---|---|
| Hypervisor | Proxmox VE | CÍLOVÝ |
| SSH přístup | nedostupný v tomto prostředí | ⚠️ |
| IP | TBD | NEZNÁMÉ |

### Virtuální stroje (plánované)

| VM ID | Název | OS | RAM | CPU | Disk | Účel | Status |
|---|---|---|---|---|---|---|---|
| VM-101 | ai-core | Ubuntu 24.04 | 8 GB | 4 | 100 GB | AI služby, Docker stack | PLÁNOVÁNO |
| VM-102 | database | Ubuntu 24.04 | 4 GB | 2 | 50 GB | PostgreSQL | PLÁNOVÁNO |
| VM-103 | monitoring | Ubuntu 24.04 | 2 GB | 2 | 20 GB | Grafana, Prometheus | PLÁNOVÁNO |

### Docker Stack (plánovaný, na ai-core VM)

| Služba | Port | Image | Status |
|---|---|---|---|
| starcore-api | 8000 | starcore-platform | PLÁNOVÁNO |
| ollama | 11434 | ollama/ollama | PLÁNOVÁNO |
| open-webui | 3000 | ghcr.io/open-webui/open-webui | PLÁNOVÁNO |
| qdrant | 6333 | qdrant/qdrant | PLÁNOVÁNO |
| redis | 6379 | redis:alpine | PLÁNOVÁNO |
| postgres | 5432 | postgres:16 | PLÁNOVÁNO |
| prometheus | 9090 | prom/prometheus | PLÁNOVÁNO |
| grafana | 3001 | grafana/grafana | PLÁNOVÁNO |

---

## EDGE PROSTŘEDÍ

| Prostředí | Status | Poznámka |
|---|---|---|
| Android / Termux | PŘIPRAVENO | Skripty existují, prostředí nedostupné |
| OSIRIS Platform | PLÁNOVÁNO | Budoucí rozšíření |
