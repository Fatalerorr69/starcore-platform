#!/data/data/com.termux/files/usr/bin/bash

STARCORE_HOME="$HOME/STARCORE"

cd "$STARCORE_HOME" || exit 1

echo "================================="
echo " STARCORE RELEASE CHECK"
echo "================================="

echo
echo "[1] Git status"

git status


echo
echo "[2] Current branch"

git branch --show-current


echo
echo "[3] Latest commit"

git log --oneline -1


echo
echo "[4] Remote"

git remote -v


echo
echo "[5] Python"

python --version


echo
echo "[6] Virtual environment"

if [ -d ".venv" ]; then
    echo "OK: .venv exists"
else
    echo "WARNING: .venv missing"
fi


echo
echo "[7] Security reports"

if [ -d "security" ]; then
    find security -type f | head -20
else
    echo "Missing security directory"
fi


echo
echo "[8] Repository size"

du -sh .


echo
echo "===== RELEASE CHECK COMPLETE ====="
