#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "=================================================="
echo " STARCORE TERMUX DEEP AUDIT"
echo "=================================================="


mkdir -p \
"$BASE/runtime/termux/audit"


REPORT="$BASE/runtime/termux/audit/termux_audit.json"


echo "[SYSTEM]"


ANDROID=$(getprop ro.product.model 2>/dev/null || echo unknown)

ANDROID_VER=$(getprop ro.build.version.release 2>/dev/null || echo unknown)


RAM=$(free -h 2>/dev/null | grep Mem || echo unknown)

DISK=$(df -h $HOME | tail -1)


PYTHON=$(python --version 2>&1 || echo missing)

NODE=$(node --version 2>&1 || echo missing)

NPM=$(npm --version 2>&1 || echo missing)


CLAUDE=$(claude --version 2>&1 || echo missing)


cat > "$REPORT" <<JSON
{
 "component":"STARCORE Termux Deep Audit",
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "device":{
    "model":"$ANDROID",
    "android":"$ANDROID_VER"
 },
 "resources":{
    "ram":"$RAM",
    "storage":"$DISK"
 },
 "runtime":{
    "python":"$PYTHON",
    "node":"$NODE",
    "npm":"$NPM",
    "claude":"$CLAUDE"
 },
 "status":"AUDITED"
}
JSON


cat "$REPORT"


echo "=================================================="
echo " AUDIT COMPLETE"
echo "=================================================="


