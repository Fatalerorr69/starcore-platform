# DELETION MANIFEST

Standard: SPOS-018 §2 | Aktualizováno: 2026-08-08

Přesný manifest všech souborů odstraněných v rámci SPOS-018.

---

## SMAZANÉ SOUBORY

```
github_intelligence/github_scanner.py
knowledge_engine/knowledge_core.py
performance/performance_analyzer.py
api_gateway/api_gateway.py
registry/commands.json
registry/modules.json
registry/sdk_registry.json
bin/control-center          (broken symlink → /data/data/com.termux/...)
bin/starcore                (Termux bash script)
bin/starcore-status         (Termux bash script)
bin/starcore-verify         (Termux bash script)
requirements.txt            (packaging/setuptools/wheel — unused)
.envrc                      (stale venv path)
config.yaml                 (stale v1.0 config)
```

## SMAZANÉ ADRESÁŘE (prázdné po smazání souborů)

```
github_intelligence/
knowledge_engine/
performance/
api_gateway/
registry/
bin/
```

## MODIFIKOVANÉ SOUBORY

```
README.md                   (odstraněna reference na config.yaml z directory tree)
```

## CELKEM

```yaml
files_deleted: 14
directories_removed: 6
files_modified: 1
total_items_affected: 15
```
