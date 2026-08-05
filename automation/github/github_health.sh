#!/data/data/com.termux/files/usr/bin/bash

echo "===== STARCORE GITHUB HEALTH ====="

echo

echo "[1] GH VERSION"
gh --version


echo

echo "[2] AUTH STATUS"
gh auth status


echo

echo "[3] REPOSITORY"
gh repo view


echo

echo "[4] REMOTE"
git remote -v


echo

echo "[5] BRANCH"
git branch -vv


echo

echo "===== COMPLETE ====="

