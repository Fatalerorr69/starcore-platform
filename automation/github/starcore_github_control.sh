#!/data/data/com.termux/files/usr/bin/bash

STARCORE_HOME="$HOME/STARCORE"
REPORT_DIR="$STARCORE_HOME/automation/github/reports"

mkdir -p "$REPORT_DIR"

REPORT="$REPORT_DIR/github_report_$(date +%Y%m%d_%H%M%S).txt"

echo "==================================" | tee "$REPORT"
echo " STARCORE GITHUB CONTROL LAYER" | tee -a "$REPORT"
echo "==================================" | tee -a "$REPORT"

cd "$STARCORE_HOME" || exit 1

echo "" | tee -a "$REPORT"
echo "[1] Repository" | tee -a "$REPORT"
git remote -v | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "[2] Branch" | tee -a "$REPORT"
git branch -vv | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "[3] Git Status" | tee -a "$REPORT"
git status | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "[4] Latest Commits" | tee -a "$REPORT"
git log --oneline -5 | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "[5] GitHub Authentication" | tee -a "$REPORT"
gh auth status | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "[6] Workflows" | tee -a "$REPORT"
gh workflow list | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "[7] Recent Runs" | tee -a "$REPORT"
gh run list --limit 10 | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "[8] Repository Info" | tee -a "$REPORT"
gh repo view | tee -a "$REPORT"

echo "" | tee -a "$REPORT"
echo "REPORT:"
echo "$REPORT" | tee -a "$REPORT"

echo ""
echo "===== COMPLETE ====="
