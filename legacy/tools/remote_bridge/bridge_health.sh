#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

mkdir -p "$BASE/runtime/termux/remote_bridge"


cat > "$BASE/runtime/termux/remote_bridge/bridge_health.json" <<JSON
{
 "component":"STARCORE Remote AI Bridge",
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "device":"$(getprop ro.product.model)",
 "architecture":"$(uname -m)",
 "python":"$(python --version 2>&1)",
 "node":"$(node --version)",
 "npm":"$(npm --version)",
 "ssh":"$(ssh -V 2>&1)",
 "status":"READY"
}
JSON


cat "$BASE/runtime/termux/remote_bridge/bridge_health.json"

