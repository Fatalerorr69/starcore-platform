# DOCUMENTATION AUDIT

Datum: 2026-08-06

---

## STAV DOKUMENTACE — PŘEHLED

| Dokument | Existuje | Kvalita | Umístění |
|---|---|---|---|
| README | ✅ | Vynikající | `platform/README.md` |
| INSTALLATION | ✅ | Dobrá | `platform/docs/installation.md` |
| ARCHITECTURE | ✅ | Vynikající | `platform/docs/architecture.md` |
| CONFIGURATION | ✅ | Dobrá | `platform/docs/development.md` |
| ROADMAP | ✅ | Částečná | `platform/README.md` (sekce) |
| CHANGELOG | ✅ | Přítomná | `platform/CHANGELOG.md` |
| SECURITY | ✅ | Dobrá | `platform/SECURITY.md`, `platform/docs/security.md` |
| API docs | ✅ | Dobrá | `platform/docs/api.md` |
| CLI docs | ✅ | Dobrá | `platform/docs/cli.md` |
| Plugin docs | ✅ | Dobrá | `platform/docs/plugins.md` |
| ADR (17) | ✅ | Vynikající | `platform/docs/adr/` |
| Testing guide | ✅ | Dobrá | `platform/docs/testing/` |
| Integration guide | ✅ | Dobrá | `platform/INTEGRATION_GUIDE.md` |
| CONTRIBUTING | ✅ | Přítomná | `platform/CONTRIBUTING.md` |

---

## DOCUMENTATION GAP REPORT

### CHYBÍ na úrovni ROOT REPOSITORY

| Chybějící dokument | Priorita | Dopad |
|---|---|---|
| `README.md` (root) | KRITICKÁ | Nový uživatel neví, co je to root repo vs `platform/` |
| `ARCHITECTURE.md` (root) | VYSOKÁ | Vztah mezi `platform/` a ostatními vrstvami není dokumentován |
| `INSTALL_SCRIPTS_GUIDE.md` | VYSOKÁ | 64 install skriptů bez centrálního průvodce |
| `INSTALL_SCRIPTS_REGISTRY.md` | VYSOKÁ | Neexistuje registr spuštěných instalací |
| `PROXMOX_DEPLOYMENT.md` | STŘEDNÍ | Jak deployovat na Proxmox |
| `DOCKER_STACK.md` | STŘEDNÍ | AI Docker stack (Ollama, OpenWebUI, Qdrant) |
| `ECOSYSTEM_MAP.md` | STŘEDNÍ | Mapa celého ekosystému (STARCORE + OSIRIS + ...) |
| `TERMUX_GUIDE.md` | NÍZKÁ | Android/Termux setup guide |

### CHYBÍ na úrovni `platform/`

| Chybějící dokument | Priorita | Dopad |
|---|---|---|
| `docs/ses/ROADMAP.md` | STŘEDNÍ | Detailní roadmap pro long-term vision |
| `docs/operations/` | STŘEDNÍ | Operations runbook |
| Deployment guide (Proxmox) | STŘEDNÍ | Jak deployovat v produkci |
| `.env.example` | NÍZKÁ | Příklad konfigurace (pokud chybí) |

---

## DOSTUPNÁ DOKUMENTACE — DETAILNÍ HODNOCENÍ

### README (platform/) — VÝBORNÁ
- Přesně popisuje aktuální stav vs. roadmap
- Tabulka komponent se stavy
- Produkční omezení dokumentována
- Quick Start příkazy funkční

### Architecture (platform/docs/architecture.md) — VÝBORNÁ
- Jasný layer diagram
- Provider SDK popsán
- Blueprint Engine vysvětlen
- Orchestrator dokumentován

### ADR (17 dokumentů) — VÝBORNÁ
- Každé architekturní rozhodnutí zdokumentováno
- Důvod, konsekvence, alternativy
- Zpětně dohledatelné

### Security — DOBRÁ
- Bandit, gitleaks dokumentovány
- Produkční omezení (RBAC, plugin sandbox) explicitně zmíněny
- Chybí: konkrétní hardening guide pro Proxmox deployment

---

## DOPORUČENÍ

### Okamžitě (Priorita 1)
1. Vytvořit `README.md` v root adresáři
2. Vytvořit `INSTALL_SCRIPTS_REGISTRY.md`

### Brzy (Priorita 2)
3. Dokumentovat vztah `platform/` ↔ ostatní vrstvy
4. Proxmox deployment guide
5. Docker AI stack guide

### Budoucnost (Priorita 3)
6. Operations runbook
7. Termux guide
