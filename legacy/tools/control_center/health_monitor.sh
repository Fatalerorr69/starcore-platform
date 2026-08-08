#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


mkdir -p "$BASE/runtime/termux/control_center"



python=$(python --version 2>&1)
node=$(node --version 2>&1)
npm=$(npm --version 2>&1)


cat > "$BASE/runtime/termux/control_center/health.json" <<JSON
{
"component":"STARCORE Termux Control Center",
"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
"runtime":{
"python":"$python",
"node":"$node",
"npm":"$npm"
},
"git":"$(git status --short)",
"status":"ONLINE"
}
JSON


cat "$BASE/runtime/termux/control_center/health.json"

