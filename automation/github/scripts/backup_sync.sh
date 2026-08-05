#!/data/data/com.termux/files/usr/bin/bash

STARCORE_HOME="$HOME/STARCORE"
BACKUP="$HOME/STARCORE_BACKUPS"

mkdir -p "$BACKUP"

DATE=$(date +%Y%m%d_%H%M%S)

echo "================================="
echo " STARCORE BACKUP"
echo "================================="


tar \
--exclude=".git" \
--exclude=".venv" \
--exclude="automation/github/reports" \
-czf "$BACKUP/starcore_$DATE.tar.gz" \
-C "$HOME" STARCORE


echo
echo "Backup created:"
echo "$BACKUP/starcore_$DATE.tar.gz"


echo
echo "===== BACKUP COMPLETE ====="
