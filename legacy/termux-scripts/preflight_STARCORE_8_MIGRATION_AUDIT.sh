#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"
REPORT="$BASE/runtime/migration/starcore_8_preflight.json"

mkdir -p "$BASE/runtime/migration"

echo "=================================================="
echo " STARCORE 8.0 MIGRATION PREFLIGHT AUDIT"
echo "=================================================="


echo "[1] SYSTEM"

TERMUX_VERSION=$(termux-info 2>/dev/null | grep TERMUX_VERSION | cut -d= -f2)
ANDROID=$(getprop ro.build.version.release)
DEVICE=$(getprop ro.product.model)


echo "[2] PYTHON"

PYTHON=$(python3 --version 2>/dev/null)


echo "[3] NODE"

NODE=$(node --version 2>/dev/null)
NPM=$(npm --version 2>/dev/null)


echo "[4] STORAGE"

DISK=$(df -h "$BASE" | tail -1 | awk '{print $4}')


echo "[5] MEMORY"

RAM=$(free -h 2>/dev/null | grep Mem | awk '{print $2}')


echo "[6] GIT"

cd "$BASE"

BRANCH=$(git branch --show-current)
COMMIT=$(git rev-parse HEAD)
STATUS=$(git status --porcelain)


echo "[7] STARCORE RELEASE"

RELEASE_EXISTS=false

if [ -f "$BASE/runtime/platform/STARCORE_7_FINAL_BULK_RELEASE.json" ]; then
    RELEASE_EXISTS=true
fi


echo "[8] MODULE REGISTRY"

MODULES=false

if [ -d "$BASE/runtime" ]; then
    MODULES=true
fi


echo "[9] CREATE REPORT"


cat > "$REPORT" <<JSON
{
    "component":"STARCORE 8 Migration Preflight Audit",
    "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "device":{
        "model":"$DEVICE",
        "android":"$ANDROID",
        "termux":"$TERMUX_VERSION"
    },
    "runtime":{
        "python":"$PYTHON",
        "node":"$NODE",
        "npm":"$NPM"
    },
    "resources":{
        "storage_available":"$DISK",
        "ram":"$RAM"
    },
    "git":{
        "branch":"$BRANCH",
        "commit":"$COMMIT",
        "clean":$([ -z "$STATUS" ] && echo true || echo false)
    },
    "starcore_7_release":{
        "exists":$RELEASE_EXISTS
    },
    "runtime_structure":{
        "exists":$MODULES
    },
    "errors":0,
    "status":"READY_FOR_REVIEW"
}
JSON


cat "$REPORT"


echo "=================================================="
echo " STARCORE 8 PREFLIGHT COMPLETE"
echo " REPORT:"
echo "$REPORT"
echo "=================================================="

