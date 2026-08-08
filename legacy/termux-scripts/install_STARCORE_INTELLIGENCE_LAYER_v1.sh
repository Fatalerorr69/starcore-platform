#!/data/data/com.termux/files/usr/bin/bash

set -e

BASE="$HOME/STARCORE"

echo "=================================================="
echo " STARCORE INTELLIGENCE LAYER v1.0"
echo "=================================================="


mkdir -p \
$BASE/intelligence/repository_map \
$BASE/intelligence/reports \
$BASE/intelligence/indexes \
$BASE/tools/intelligence



############################################
# REPOSITORY SCANNER
############################################


cat > $BASE/tools/intelligence/repo_scan.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


mkdir -p \
$BASE/intelligence/repository_map


echo "========== STARCORE REPOSITORY SCAN =========="


find "$BASE" \
-type f \
-not -path "*/.git/*" \
> "$BASE/intelligence/repository_map/files.txt"



FILES=$(wc -l < "$BASE/intelligence/repository_map/files.txt")


DIRS=$(find "$BASE" \
-type d \
-not -path "*/.git/*" | wc -l)



cat > "$BASE/intelligence/repository_map/repository_map.json" <<JSON
{
"component":"STARCORE Repository Intelligence",
"files":"$FILES",
"directories":"$DIRS",
"workspace":"$BASE",
"status":"READY"
}
JSON


cat "$BASE/intelligence/repository_map/repository_map.json"


SH


chmod +x \
$BASE/tools/intelligence/repo_scan.sh




############################################
# GIT INTELLIGENCE
############################################


cat > $BASE/tools/intelligence/git_intelligence.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


mkdir -p \
$BASE/intelligence/reports


cd "$BASE"


cat > "$BASE/intelligence/reports/git_status.json" <<JSON
{
"branch":"$(git branch --show-current)",
"commit":"$(git rev-parse HEAD)",
"remote":"$(git remote get-url origin)",
"changes":"$(git status --short | wc -l)",
"status":"READY"
}
JSON


cat "$BASE/intelligence/reports/git_status.json"

SH


chmod +x \
$BASE/tools/intelligence/git_intelligence.sh




############################################
# PROJECT HEALTH
############################################


cat > $BASE/tools/intelligence/project_health.sh <<'SH'
#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "========== STARCORE PROJECT HEALTH =========="


echo ""

echo "[RUNTIME]"

python --version
node --version
npm --version


echo ""

echo "[GIT]"

cd "$BASE"

git status --short


echo ""

echo "[STRUCTURE]"

find "$BASE" -maxdepth 1 -type d | sort


SH


chmod +x \
$BASE/tools/intelligence/project_health.sh



############################################
# RUN


$BASE/tools/intelligence/repo_scan.sh

$BASE/tools/intelligence/git_intelligence.sh


echo ""

echo "[GIT COMMIT]"


cd "$BASE"

git add .

git commit \
-m "Add STARCORE Intelligence Layer v1.0" || true



echo "=================================================="
echo " INTELLIGENCE LAYER COMPLETE"
echo " STATUS READY"
echo "=================================================="


