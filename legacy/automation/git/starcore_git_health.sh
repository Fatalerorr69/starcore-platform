#!/data/data/com.termux/files/usr/bin/bash

echo "===== STARCORE GIT HEALTH ====="

cd ~/STARCORE || exit 1


echo
echo "[1] ROOT"
pwd


echo
echo "[2] GIT ROOT"
git rev-parse --show-toplevel


echo
echo "[3] REMOTE"
git remote -v


echo
echo "[4] BRANCH"
git branch -vv


echo
echo "[5] STATUS"
git status


echo
echo "[6] LAST COMMITS"
git log --oneline -5


echo
echo "[7] NESTED REPOSITORIES"

find . -name ".git" -type d


echo
echo "===== COMPLETE ====="

