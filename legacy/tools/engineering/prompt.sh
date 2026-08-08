#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

TYPE="$1"

OUT="$BASE/prompts/generated"

mkdir -p "$OUT"


case "$TYPE" in

audit)

cat > "$OUT/audit.md" <<EOT
# STARCORE FULL AUDIT

Analyze:

$BASE

Tasks:

- architecture
- duplicates
- security
- optimization

No modifications.
EOT

;;

proxmox)

cat > "$OUT/proxmox.md" <<EOT
# STARCORE PROXMOX OPERATOR

Host:
fatalab

VM:
100 FataLab-Core

Services:

- Ollama
- OpenWebUI
- Qdrant
- Docker

Perform infrastructure audit.
EOT

;;

coding)

cat > "$OUT/coding.md" <<EOT
# STARCORE DEVELOPMENT MODE

Rules:

Backup first.

Analyze.

Modify.

Test.

Commit.
EOT

;;

*)

echo "Usage:"
echo "audit"
echo "proxmox"
echo "coding"

;;

esac

echo "PROMPT READY"
