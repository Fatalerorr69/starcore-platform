#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "========== STARCORE PROJECT HEALTH =========="


echo ""

echo "[RUNTIME]"

python --version
node --version
npm --version


echo ""

echo "[GIT]"

cd "$BASE"

git status --short


echo ""

echo "[STRUCTURE]"

find "$BASE" -maxdepth 1 -type d | sort


