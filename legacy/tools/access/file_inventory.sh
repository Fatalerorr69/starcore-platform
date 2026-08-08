#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

mkdir -p "$BASE/runtime/access"


find "$BASE" \
-type f \
-not -path "*/.git/*" \
> "$BASE/runtime/access/file_inventory.txt"


COUNT=$(wc -l < "$BASE/runtime/access/file_inventory.txt")


cat > "$BASE/runtime/access/file_inventory.json" <<JSON
{
 "component":"STARCORE File Intelligence",
 "files":"$COUNT",
 "status":"READY"
}
JSON


cat "$BASE/runtime/access/file_inventory.json"

