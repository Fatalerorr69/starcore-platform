# TECHNOLOGY PROFILE — Docker

```yaml
name: Docker
purpose: Kontejnerizace — hostuje AI Stack (Ollama, OpenWebUI, Qdrant, Redis) a lokální vývoj
category: Infrastructure / Containers
version: "29.3.1 (dostupná v tomto prostředí)"
official_source: SRC-DOCKER-001
```

## DEPENDENCIES
Linux kernel s cgroups/namespaces podporou. docker-py (Python klient) pro STARCORE integraci.

## COMPATIBILITY
Aktivní v aktuálním Claude Code prostředí i cílovém Proxmox AI Core VM.

## INSTALLATION
Aktuální prostředí: preinstalováno (29.3.1). Proxmox VM: standardní Docker Engine instalace na Ubuntu 24.04 (plánováno).

## CONFIGURATION
STARCORE Docker Provider čte Docker socket/API dle standardní docker-py konfigurace (`DOCKER_HOST` env var nebo default socket).

## SECURITY
- Docker socket přístup = root-ekvivalentní — omezit na trusted procesy
- Image scanning doporučen (mimo scope aktuální implementace)
- Rootless mode zvážit pro produkci

## AUTOMATION
STARCORE Docker Provider (`platform/packages/providers`): connect, health, list_resources (containers/images), execute (create/start/stop/remove).

## INTEGRATION
- Provider SDK — MOD-005 v MODULE_REGISTRY
- Plánovaný AI Stack: `docker/ai-stack/docker-compose.yml` (Bootstrap 00 Fáze 2, zatím nevytvořeno)

## STARCORE_USAGE
1. Lokální dev (platform `docker-compose.yml`)
2. Cílový AI Stack na Proxmox AI Core VM (Ollama, OpenWebUI, Qdrant, Redis, Postgres)

## RISKS
- Bez resource limitů může kontejner vyčerpat VM zdroje
- Plugin systém STARCORE není sandboxován (ADR-011) — netýká se přímo Dockeru, ale podobné riziko modelu

## UPDATE_POLICY
Sledovat Docker Engine LTS/stable releases; review při upgrade docker-py závislosti.
```
