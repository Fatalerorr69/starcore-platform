# STARCORE INSTALLER STUDIO — ARCHITECTURE PLAN

Standard: SPOS-008 §8, §18 | Aktualizováno: 2026-08-06

> **Toto je NÁVRH, ne implementace.** README platformy sám řadí "Installer Studio" do sekce "Roadmap / Vision (Not Started)". Tento dokument navrhuje architekturu pro budoucí implementaci, nevytváří kód.

---

## PROČ TEĎ NEBUDOVAT

Dle SES-000 P001 (Architecture First) a P003 (Automation First, ale ne předčasně) — Installer Studio vyžaduje nejprve funkční Track A deployment (Proxmox VM + Docker AI Stack), který **dosud neexistuje reálně** (viz SPOS-007: 0 reálných VM, Docker daemon zde neběží). Stavět "Studio" nad neexistující infrastrukturou by bylo předčasné.

---

## NAVRHOVANÁ STRUKTURA (§8)

```
platform/installer/          ← nový package, analogický k packages/blueprints
├── profiles/
│   ├── dev.yaml              ← lokální vývoj (SQLite, no AI stack)
│   ├── homelab.yaml           ← Proxmox VM + Docker AI Stack (Ollama/Qdrant)
│   └── edge.yaml               ← Android/Termux (nahradí stub install_*.sh)
├── modules/
│   ├── proxmox_provision.py    ← využívá existující packages/providers/proxmox
│   ├── docker_stack.py          ← využívá existující packages/providers/docker
│   └── ai_stack.py               ← Ollama/Qdrant/OpenWebUI setup (MOD-100..102, plánováno)
├── templates/
│   ├── cloud-init/                ← VM cloud-init šablony
│   └── docker-compose/             ← per-profile compose overrides
├── validators/
│   └── preflight.py                 ← requirements check (CPU/RAM/disk před instalací)
└── reports/
    └── (generované instalační reporty)
```

**Klíčový princip:** `installer/modules/*` **znovupoužívají** existující `provider_sdk`/`providers` (MOD-004..006) — Installer Studio je orchestrační vrstva nad již otestovaným Provider SDK, ne nová implementace Proxmox/Docker logiky.

---

## INSTALLATION PIPELINE (§7)

```
CHECK REQUIREMENTS   → validators/preflight.py (CPU/RAM/disk/network)
       ↓
PREPARE SYSTEM        → cloud-init / apt (Proxmox VM) nebo Termux pkg (edge)
       ↓
INSTALL DEPENDENCIES   → uv sync (platform) / apt/pkg (systém)
       ↓
DEPLOY SERVICES          → docker compose up (dle profilu)
       ↓
RUN TESTS                  → starcore doctor / health check
       ↓
GENERATE REPORT              → installer/reports/<timestamp>.md
```

---

## BUDOUCÍ FUNKCE (§8, mimo fázi 1)

| Funkce | Priorita |
|---|---|
| CLI (`starcore installer run <profile>`) | P1 — první přírůstek |
| Validators (preflight checks) | P1 |
| GUI | P3 — daleká budoucnost |
| ISO / LXC templates | P3 |
| Docker images (pre-baked AI stack) | P2 |

---

## VZTAH K install_*.sh (Track B)

Installer Studio **nenahrazuje** 65 historických `install_*.sh` skriptů automaticky — ty zůstávají jako archivní artefakt (viz DEPLOYMENT_ARCHITECTURE.md). Pokud bude v budoucnu potřeba reálný Android/Termux edge deployment, `profiles/edge.yaml` + `modules/` ho nahradí funkční implementací, ne stub generátory.

---

## DOPORUČENÝ POŘADÍ IMPLEMENTACE (mimo scope tohoto kroku)

1. Nejprve: reálný Proxmox přístup (uživatel musí poskytnout credentials)
2. Docker AI Stack (MOD-100, `docker/ai-stack/docker-compose.yml`) — viz IMPROVEMENT_ROADMAP Fáze 2
3. `installer/profiles/homelab.yaml` + `modules/proxmox_provision.py` — až po ověření 1-2 fungují ručně
4. CLI integrace (`starcore installer`)
