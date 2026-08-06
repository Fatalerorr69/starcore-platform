# PROJECT REGISTRY

Aktualizováno: 2026-08-06

---

## PROJEKT: STARCORE AI PLATFORM

| Pole | Hodnota |
|---|---|
| Název | STARCORE AI Platform |
| Verze | 0.6.0 (platform), 1.0 (ekosystém) |
| Status | Aktivní vývoj |
| Repository | `Fatalerorr69/starcore-platform` |
| Branch (main) | `main` |
| Branch (bootstrap) | `claude/starcore-ai-bootstrap-fkyb96` |
| Autor | Jakub Krajča |
| Licence | Apache-2.0 |

---

## SOUČÁSTI EKOSYSTÉMU

| Modul | Adresář | Status |
|---|---|---|
| Platform API | `platform/` | Aktivní (v0.6.0) |
| Agent Framework | `agents/` | Aktivní |
| Runtime State | `runtime/` | Aktivní |
| Knowledge Base | `knowledge/` | Aktivní |
| Security Layer | `security/` | Aktivní |
| Control Center | `control_center/` | Aktivní |
| Intelligence Layer | `intelligence/` | Aktivní |
| AI Core | `ai_core/` | Aktivní |
| Automation | `automation/` | Aktivní |
| Android/Termux | `install_TERMUX_*.sh` | Připraveno |
| OSIRIS | (budoucí) | Plánováno |

---

## CÍLOVÁ INFRASTRUKTURA

| Vrstva | Technologie | Status |
|---|---|---|
| Hypervisor | Proxmox VE | Cílový |
| VM / LXC | Ubuntu 24.04 | Cílový |
| Containers | Docker | Aktivní |
| LLM Inference | Ollama | Plánováno |
| Vector DB | Qdrant | Plánováno |
| Web UI | OpenWebUI | Plánováno |
| Cache | Redis | Plánováno |
| Monitoring | Prometheus + Grafana | Plánováno |
