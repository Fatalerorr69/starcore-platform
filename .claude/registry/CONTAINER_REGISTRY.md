# CONTAINER REGISTRY

Standard: SPOS-007 §7 | Aktualizováno: 2026-08-06

Audit `platform/docker-compose.yml` (zdroj pravdy) + živé ověření (`docker ps` selhalo — Docker daemon v tomto prostředí neběží, jen CLI binárka je nainstalována).

---

## AKTIVNÍ SLUŽBY (výchozí `docker compose up`)

### SERVICE: api
```yaml
service: api
image: "build: . (Dockerfile v platform/)"
port: "8000:8000"
dependency: "SQLite (starcore-data volume) nebo STARCORE_DATABASE_URL"
status: DEFINOVÁNO (docker-compose.yml), NESPUŠTĚNO (Docker daemon nedostupný v tomto prostředí)
notes: "Mountuje /var/run/docker.sock — root-ekvivalentní přístup k hostu (zdokumentované riziko v compose souboru)"
```

## SCAFFOLD SLUŽBY (profil `scaffold`, needefaultně spuštěné)

### SERVICE: postgres
```yaml
service: postgres
image: "postgres:17"
port: "5432:5432"
dependency: "STARCORE_POSTGRES_PASSWORD env var"
status: SCAFFOLDING — "Postgres/Redis/NATS-backed features nejsou zatím zapojeny do aplikace" (dle komentáře v compose souboru)
```

### SERVICE: redis
```yaml
service: redis
image: "redis:8"
port: "6379:6379"
status: SCAFFOLDING
```

### SERVICE: nats
```yaml
service: nats
image: "nats:2.10"
port: "4222:4222"
status: SCAFFOLDING
```

---

## PLÁNOVANÉ SLUŽBY (Docker AI Stack, MOD-100, nevytvořeno)

| Service | Image | Účel | Status |
|---|---|---|---|
| ollama | ollama/ollama | LLM inference | PLÁNOVÁNO |
| open-webui | ghcr.io/open-webui/open-webui | Chat UI | PLÁNOVÁNO |
| qdrant | qdrant/qdrant | Vector DB | PLÁNOVÁNO |

---

## ŽIVĚ OVĚŘENO

```
$ docker ps -a
failed to connect to the docker API at unix:///var/run/docker.sock:
dial unix /var/run/docker.sock: connect: no such file or directory
```

**Korekce dřívějšího Bootstrap 00 zjištění:** Report tehdy uváděl Docker jako "Aktivní" v tomto prostředí na základě `docker --version`. Live test nyní potvrzuje: **binárka je nainstalována, ale daemon neběží** — žádné kontejnery zde nelze spravovat. Opraveno.

## STATISTIKY

```yaml
services_defined: 4 (api, postgres, redis, nats)
services_running_here: 0 (Docker daemon nedostupný)
services_planned: 3 (AI stack)
```
