#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"

mkdir -p "$BASE/runtime/termux"


echo "=================================================="
echo " TERMUX PACKAGE HEALTH"
echo "=================================================="


pkg update


pkg list-upgradable > \
"$BASE/runtime/termux/package_updates.txt" 2>&1 || true


dpkg --audit > \
"$BASE/runtime/termux/dpkg_audit.txt" 2>&1 || true


cat > "$BASE/runtime/termux/package_health.json" <<JSON
{
 "component":"Termux Package Health",
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "upgrade_check":true,
 "dpkg_check":true,
 "status":"complete"
}
JSON


cat "$BASE/runtime/termux/package_health.json"


echo "=================================================="


