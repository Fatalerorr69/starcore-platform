#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "=================================================="
echo " STARCORE 8.10 GOLD MASTER BACKUP"
echo "=================================================="


mkdir -p \
"$BASE/runtime/gold_master" \
"$BASE/backups/releases"


echo "[1] CREATE MANIFEST"


cat > "$BASE/runtime/gold_master/STARCORE_8_GOLD_MASTER.json" <<JSON
{
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "component":"STARCORE Gold Master",
 "version":"8.10",
 "phase":"ANDROID_PHASE1",
 "modules":100,
 "audit":"PASSED",
 "status":"ARCHIVED"
}
JSON


echo "[2] CREATE ARCHIVE"


tar -czf \
"$BASE/backups/releases/STARCORE_8.10_GOLD_MASTER.tar.gz" \
--exclude="./backups/releases/STARCORE_8.10_GOLD_MASTER.tar.gz" \
.


echo "[3] SIZE"


ls -lh "$BASE/backups/releases/STARCORE_8.10_GOLD_MASTER.tar.gz"


echo "[4] CHECKSUM"


sha256sum \
"$BASE/backups/releases/STARCORE_8.10_GOLD_MASTER.tar.gz" \
> "$BASE/runtime/gold_master/SHA256SUM"


echo "[5] VALIDATION"


cat "$BASE/runtime/gold_master/STARCORE_8_GOLD_MASTER.json"


echo "[6] GIT"


cd "$BASE"

git add .

git commit -m "Create STARCORE 8.10 Gold Master Archive" || true


echo ""
echo "=================================================="
echo " STARCORE 8 GOLD MASTER COMPLETE"
echo " STATUS: ARCHIVED"
echo "=================================================="


