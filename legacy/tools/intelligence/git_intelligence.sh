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

