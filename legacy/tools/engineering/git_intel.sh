#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "========== GIT INTELLIGENCE =========="

git -C "$BASE" status

echo

git -C "$BASE" log --oneline -20
