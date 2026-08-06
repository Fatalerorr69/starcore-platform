# COMPUTE REGISTRY (VM/LXC)

Standard: SPOS-007 §6 | Aktualizováno: 2026-08-06

Živě ověřeno: `starcore diagnose --json` → `proxmox.nodes: []`, `proxmox.resources: {}` — **žádné VM/LXC dosažitelné**, protože Proxmox API není nakonfigurováno v tomto prostředí. Platform **umí** VM/LXC spravovat (Provider SDK, MOD-006) — jen zde není co spravovat.

---

## PLÁNOVANÉ INSTANCE (dle INFRASTRUCTURE_REGISTRY.md z Bootstrap 00, dosud nevytvořeny)

### VM-101 — ai-core
```yaml
instance_id: VM-101
type: VM
host: HOST-002 (Proxmox, nedostupný)
os: "Ubuntu 24.04"
cpu: 4
ram: "8 GB"
storage: "100 GB"
purpose: "AI služby (Ollama, OpenWebUI, Qdrant, Redis), STARCORE API"
status: PLÁNOVÁNO — NEVYTVOŘENO
```

### VM-102 — database
```yaml
instance_id: VM-102
type: VM
host: HOST-002 (Proxmox, nedostupný)
os: "Ubuntu 24.04"
cpu: 2
ram: "4 GB"
storage: "50 GB"
purpose: PostgreSQL
status: PLÁNOVÁNO — NEVYTVOŘENO
```

### VM-103 — monitoring
```yaml
instance_id: VM-103
type: VM
host: HOST-002 (Proxmox, nedostupný)
os: "Ubuntu 24.04"
cpu: 2
ram: "2 GB"
storage: "20 GB"
purpose: "Prometheus, Grafana"
status: PLÁNOVÁNO — NEVYTVOŘENO
```

---

## ŽIVĚ OVĚŘENO

```json
"proxmox": {
  "nodes": [],
  "storage": [],
  "resources": {},
  "orphaned_resources": []
}
```

Zdroj kódu pro budoucí reálnou správu: `platform/packages/providers/proxmox` (MOD-006, implementuje `BaseProvider`, otestováno mocky proxmoxer, ne proti reálnému Proxmoxu).

## STATISTIKY

```yaml
instances_total: 0 (reálně)
instances_planned: 3
```
