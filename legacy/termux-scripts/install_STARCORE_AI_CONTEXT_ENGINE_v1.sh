#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "=============================================="
echo " STARCORE AI CONTEXT ENGINE v1.0"
echo "=============================================="


mkdir -p \
$BASE/config \
$BASE/runtime/sessions \
$BASE/tools/context


cat > $BASE/config/ai_context.yaml <<YAML

project:
  name: STARCORE
  version: 1.0


workspace:
  local: ~/STARCORE


github:
  repository: Fatalerorr69/starcore-platform
  branch: main


infrastructure:

  proxmox:
    host: fatalab


  vm:
    id: 100
    name: FataLab-Core


services:

  ollama:
    port:11434

  openwebui:
    port:3000

  qdrant:
    port:6333


agents:

 permissions:
  - read
  - analyze
  - modify
  - commit


rules:

 - backup_before_change
 - document_changes
 - commit_after_success


YAML



cat > $BASE/tools/context/context_show.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash

cat ~/STARCORE/config/ai_context.yaml

SH


chmod +x \
$BASE/tools/context/context_show.sh



cat > $BASE/runtime/sessions/context_engine.json <<JSON

{
"component":"STARCORE AI Context Engine",
"version":"1.0",
"status":"READY"
}

JSON



cd $BASE

git add .

git commit \
-m "Add STARCORE AI Context Engine" || true


echo "=============================================="
echo " AI CONTEXT ENGINE COMPLETE"
echo "=============================================="

