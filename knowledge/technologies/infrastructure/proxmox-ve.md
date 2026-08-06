# TECHNOLOGY PROFILE — Proxmox VE

```yaml
name: Proxmox VE
purpose: Open-source hypervisor (KVM + LXC) — cílová platforma pro STARCORE infrastrukturu
category: Infrastructure / Hypervisor
version: "8.x"
official_source: SRC-PROXMOX-001
```

## DEPENDENCIES
Debian-based host OS, KVM (hardware virtualizace), ZFS/LVM/Ceph (storage backends).

## COMPATIBILITY
Podporuje VM (plná virtualizace) i LXC (kontejnery). API dostupné přes REST (proxmoxer knihovna v Pythonu).

## INSTALLATION
Instalace na bare-metal Debian, nebo dedikovaný Proxmox ISO installer. Mimo scope tohoto AI prostředí (vyžaduje fyzický/vzdálený přístup k hardware).

## CONFIGURATION
API token nebo user/password autentizace. STARCORE Platform očekává API endpoint + credentials v `.env` (`STARCORE_PROXMOX_*`, viz `platform/packages/providers`).

## SECURITY
- API tokeny s omezenými právy (role-based)
- Firewall na úrovni Proxmox datacentra
- Pravidelné aktualizace host OS

## AUTOMATION
STARCORE Proxmox Provider (`platform/packages/providers`) implementuje: connect, health, list_resources (VM/LXC), execute (start/stop/shutdown/clone/snapshot).
CLI: `starcore proxmox discover`, `starcore snapshot create/list/delete/rollback`.

## INTEGRATION
- Provider SDK (`BaseProvider` implementace) — viz MOD-006 v MODULE_REGISTRY
- Blueprint Engine — template aliasy (`config: {template: "ubuntu-24.04"}`)

## STARCORE_USAGE
Cílová platforma pro AI Core VM (Ollama + OpenWebUI + Qdrant + Redis Docker stack). Zatím NEDOSTUPNÁ v aktuálním Claude Code prostředí (chybí SSH/API přístup).

## RISKS
- Bez SSH/API přístupu nelze validovat konfiguraci v tomto prostředí
- Single point of failure bez clusteru

## UPDATE_POLICY
Review při každé major verzi Proxmox nebo změně STARCORE Proxmox Provider kódu.
```
