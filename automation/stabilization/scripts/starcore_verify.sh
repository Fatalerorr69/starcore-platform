#!/data/data/com.termux/files/usr/bin/bash

ROOT="$HOME/STARCORE"
REPORT="$ROOT/automation/stabilization/reports/verify_$(date +%Y%m%d_%H%M%S).txt"

mkdir -p "$(dirname "$REPORT")"

exec > >(tee "$REPORT") 2>&1

echo "==============================================="
echo " STARCORE VERIFY"
echo "==============================================="

cd "$ROOT" || exit 1

echo
echo "[1] PROJECT ROOT"
pwd

echo
echo "[2] STRUCTURE"

for DIR in \
bin \
core \
automation \
security \
platform \
ai \
agents \
backup \
logs \
runtime \
workspace
do
    if [ -d "$DIR" ]; then
        echo "OK DIR: $DIR"
    else
        echo "MISSING DIR: $DIR"
    fi
done


echo
echo "[3] MAIN CLI"

if [ -x bin/starcore ]; then
    echo "OK: bin/starcore executable"
else
    echo "FIX REQUIRED: bin/starcore"
fi


echo
echo "[4] GIT"

git status

echo
git branch -vv

echo
git remote -v


echo
echo "[5] GITHUB CLI"

if command -v gh >/dev/null; then
    gh --version | head -n1
else
    echo "gh missing"
fi


echo
echo "[6] PYTHON"

python --version 2>/dev/null || true
python3 --version 2>/dev/null || true


echo
echo "[7] VENV"

if [ -d .venv ]; then
    echo "OK .venv exists"
else
    echo "NO .venv detected"
fi


echo
echo "[8] SCRIPT PERMISSIONS"

find automation -type f -name "*.sh" | while read FILE
do
    if [ -x "$FILE" ]; then
        echo "EXEC OK $FILE"
    else
        echo "NOT EXEC $FILE"
    fi
done


echo
echo "[9] PYTHON FILE COUNT"

find . -name "*.py" | wc -l


echo
echo "[10] PROJECT SIZE"

du -sh .


echo
echo "==============================================="
echo " VERIFY COMPLETE"
echo "REPORT:"
echo "$REPORT"
echo "==============================================="

