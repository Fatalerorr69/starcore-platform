#!/data/data/com.termux/files/usr/bin/bash

STARCORE_HOME="$HOME/STARCORE"
REPORT_DIR="$STARCORE_HOME/automation/github/reports"

mkdir -p "$REPORT_DIR"

REPORT="$REPORT_DIR/repository_audit_$(date +%Y%m%d_%H%M%S).txt"

cd "$STARCORE_HOME" || exit 1

{
echo "================================="
echo " STARCORE REPOSITORY AUDIT "
echo "================================="

echo
echo "[1] DATE"
date

echo
echo "[2] GIT STATUS"
git status

echo
echo "[3] BRANCH"
git branch -vv

echo
echo "[4] LAST COMMITS"
git log --oneline -10

echo
echo "[5] REMOTE"
git remote -v

echo
echo "[6] GITHUB AUTH"
gh auth status

echo
echo "[7] WORKFLOWS"
gh workflow list

echo
echo "[8] ACTION RUNS"
gh run list --limit 10

echo
echo "[9] WORKFLOW FILES"
find .github/workflows -type f

echo
echo "[10] AUTOMATION"
find automation/github -type f

echo
echo "[11] SECURITY FILES"
find security -type f 2>/dev/null

echo
echo "[12] SIZE"
du -sh .

echo
echo "================================="
echo " AUDIT COMPLETE "
echo "================================="

} | tee "$REPORT"


echo
echo "REPORT:"
echo "$REPORT"

