#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "========== SSH HEALTH =========="


SSH_VERSION=$(ssh -V 2>&1)


cat > "$BASE/runtime/termux/remote_bridge/ssh_health.json" <<JSON
{
 "component":"STARCORE SSH Connector",
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "ssh":"$SSH_VERSION",
 "status":"READY"
}
JSON


cat "$BASE/runtime/termux/remote_bridge/ssh_health.json"

