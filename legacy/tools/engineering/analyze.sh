#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "========== STARCORE ANALYSIS =========="


echo
echo "[PYTHON FILES]"

find "$BASE" \
-type f \
-name "*.py" \
-not -path "*/.venv/*" \
-not -path "*/__pycache__/*" \
| wc -l


echo
echo "[SHELL TOOLS]"

find "$BASE/tools" \
-type f \
-name "*.sh" \
| wc -l


echo
echo "[GIT]"

git -C "$BASE" status --short


echo
echo "[DIRECTORIES]"

find "$BASE" \
-maxdepth 1 \
-type d \
-not -name ".git" \
| sort

