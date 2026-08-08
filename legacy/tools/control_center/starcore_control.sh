#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "======================================"
echo " STARCORE TERMUX CONTROL CENTER"
echo "======================================"


echo ""

echo "[1] SYSTEM"

uname -a


echo ""

echo "[2] RUNTIME"

python --version
node --version
npm --version


echo ""

echo "[3] CLAUDE"

claude --version || echo "CLAUDE OFFLINE"


echo ""

echo "[4] GIT"

git status


echo ""

echo "======================================"

