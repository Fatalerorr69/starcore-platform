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


