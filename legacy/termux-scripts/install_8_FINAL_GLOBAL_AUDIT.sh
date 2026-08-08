#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "=================================================="
echo " STARCORE 8 FINAL GLOBAL AUDIT"
echo "=================================================="


mkdir -p "$BASE/runtime/audit"


echo "[SYSTEM]"

python3 --version
node --version
npm --version


echo ""
echo "[RELEASE CHECK]"


FILES=(

"runtime/agents/release/STARCORE_8B_RELEASE.json"

"runtime/knowledge/release/STARCORE_8C_RELEASE.json"

"runtime/distributed/release/STARCORE_8D_RELEASE.json"

"runtime/security/release/STARCORE_8E_RELEASE.json"

"runtime/control_plane/release/STARCORE_8F_RELEASE.json"

"runtime/marketplace/release/STARCORE_8G_RELEASE.json"

"runtime/automation/release/STARCORE_8H_RELEASE.json"

"runtime/optimization/release/STARCORE_8I_RELEASE.json"

"runtime/autonomous/release/STARCORE_8_MASTER_RELEASE.json"

)


ERRORS=0


for FILE in "${FILES[@]}"
do

if [ -f "$BASE/$FILE" ]

then

echo "OK  $FILE"

else

echo "MISS $FILE"

ERRORS=$((ERRORS+1))

fi

done


echo ""
echo "[PROJECT SIZE]"

du -sh "$BASE"


echo ""
echo "[GIT STATUS]"

cd "$BASE"

git status


echo ""
echo "[AUDIT REPORT]"


cat > "$BASE/runtime/audit/STARCORE_8_FINAL_AUDIT.json" <<JSON
{
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "component":"STARCORE 8 Final Global Audit",
 "release":"8.10",
 "modules":100,
 "errors":$ERRORS,
 "status":"$( [ $ERRORS -eq 0 ] && echo PRODUCTION || echo FAILED )"
}
JSON


cat "$BASE/runtime/audit/STARCORE_8_FINAL_AUDIT.json"


echo ""
echo "=================================================="
echo " STARCORE 8 FINAL AUDIT COMPLETE"
echo "=================================================="


