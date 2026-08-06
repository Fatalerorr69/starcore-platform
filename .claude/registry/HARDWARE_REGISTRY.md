# HARDWARE REGISTRY

Standard: SPOS-007 §4 | Aktualizováno: 2026-08-06

Živě ověřeno přes `starcore diagnose --json` a systémové příkazy. Proxmox hardware **nedosažitelný** z tohoto prostředí (chybí credentials) — registrován jako PLÁNOVANÝ, ne fabrikovaný.

---

### HOST-001 — Claude Code Remote Container (aktuální prostředí)
```yaml
host_id: HOST-001
type: Cloud container (ephemeral)
cpu: "Intel Xeon @ 2.80GHz"
ram: "15 GiB"
gpu: none
storage: "252 GB celkem, ~30 GB dostupných"
network: "Agent proxy (outbound HTTPS)"
location: "Claude Code Remote (cloud, přesná lokace neznámá)"
status: ACTIVE
verified: "2026-08-06, starcore diagnose --json: runtime_environment=local"
```

### HOST-002 — Proxmox Host (cílový)
```yaml
host_id: HOST-002
type: Proxmox VE hypervisor
cpu: NEZNÁMÉ — vyžaduje STARCORE_PROXMOX_HOST/USER/TOKEN_NAME/TOKEN_VALUE
ram: NEZNÁMÉ
gpu: NEZNÁMÉ
storage: NEZNÁMÉ
network: NEZNÁMÉ
location: NEZNÁMÉ (uživatelův homelab, dle SES-000 kontextu)
status: PLÁNOVÁNO — NEDOSTUPNÝ
verified: "2026-08-06, starcore diagnose --json: provider.proxmox=error (Failed to connect to Proxmox API), config.proxmox=warning (credentials not fully set)"
```

### HOST-003 — Android Edge Node (OSIRIS)
```yaml
host_id: HOST-003
type: Samsung Android + Termux
cpu: NEZNÁMÉ
ram: NEZNÁMÉ
status: PŘIPRAVENO (skripty existují: install_TERMUX_*.sh), NEDOSTUPNÉ pro live audit
```

---

## STATISTIKY

```yaml
hosts_total: 3
hosts_active: 1
hosts_planned_unreachable: 2
```
