#!/data/data/com.termux/files/usr/bin/bash

STARCORE_HOME="$HOME/STARCORE"

cd "$STARCORE_HOME" || exit 1

echo "================================="
echo " STARCORE SECURITY SCAN"
echo "================================="


echo
echo "[1] Check secrets patterns"

grep -RniE "ghp_|github_pat_|api_key|password|secret" . \
--exclude-dir=.git \
--exclude-dir=.venv \
2>/dev/null | head -50


echo
echo "[2] Git ignored files"

git status --ignored | head -100


echo
echo "[3] Security directory"

find security -type f 2>/dev/null


echo
echo "[4] Python cache"

find . -name "__pycache__" | head -20


echo
echo "===== SECURITY SCAN COMPLETE ====="
