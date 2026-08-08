#!/data/data/com.termux/files/usr/bin/bash

STARCORE_HOME="$HOME/STARCORE"
REPORT_DIR="$STARCORE_HOME/automation/github/reports"

mkdir -p "$REPORT_DIR"

REPORT="$REPORT_DIR/starcore_doctor_$(date +%Y%m%d_%H%M%S).txt"

cd "$STARCORE_HOME" || exit 1

exec > >(tee "$REPORT") 2>&1

echo "==============================================="
echo " STARCORE DOCTOR"
echo "==============================================="

echo
echo "[1] DATE"
date

echo
echo "[2] SYSTEM"
uname -a

echo
echo "[3] TERMUX"
termux-info 2>/dev/null || true

echo
echo "[4] PYTHON"
python --version 2>/dev/null
python3 --version 2>/dev/null

echo
echo "[5] GIT"
git --version

echo
echo "[6] GITHUB CLI"
gh --version | head -n 1

echo
echo "[7] NETWORK"

echo "- github api"
curl -Is https://api.github.com | head -n 1

echo
echo "- dns"
if command -v dig >/dev/null; then
    dig +short github.com
elif command -v nslookup >/dev/null; then
    nslookup github.com
else
    ping -c 1 github.com
fi

echo
echo "[8] GITHUB AUTH"
gh auth status

echo
echo "[9] GIT STATUS"
git status

echo
echo "[10] BRANCH"
git branch -vv

echo
echo "[11] LAST COMMITS"
git log --oneline -10

echo
echo "[12] REMOTE"
git remote -v

echo
echo "[13] WORKFLOWS"
gh workflow list

echo
echo "[14] LAST RUNS"
gh run list --limit 10

echo
echo "[15] WORKFLOW FILES"
find .github/workflows -type f

echo
echo "[16] AUTOMATION"
find automation/github -type f

echo
echo "[17] SECURITY"
find security -type f 2>/dev/null

echo
echo "[18] REPOSITORY SIZE"
du -sh .

echo
echo "[19] DISK"
df -h

echo
echo "[20] GIT FSCK"
git fsck --full

echo
echo "[21] VERIFY HEAD"
git rev-parse HEAD

echo
echo "[22] REMOTE HEAD"
git ls-remote origin HEAD

echo
echo "[23] PENDING COMMITS"
git status -sb

echo
echo "==============================================="
echo " STARCORE DOCTOR COMPLETE"
echo "==============================================="

echo
echo "REPORT SAVED:"
echo "$REPORT"

