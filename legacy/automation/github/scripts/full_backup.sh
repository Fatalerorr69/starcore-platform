#!/data/data/com.termux/files/usr/bin/bash

DEST="$HOME/STARCORE_BACKUPS"

mkdir -p "$DEST"

FILE="$DEST/starcore_$(date +%Y%m%d_%H%M%S).tar.gz"

tar \
--exclude=.git \
--exclude=.venv \
-czf "$FILE" \
"$HOME/STARCORE"

echo
echo "Backup created:"
echo "$FILE"

ls -lh "$FILE"
