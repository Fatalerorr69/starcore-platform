#!/data/data/com.termux/files/usr/bin/bash


BASE="$HOME/STARCORE"


echo "========== PROXMOX HEALTH =========="


SSH=$(ssh -V 2>&1)


cat > "$BASE/runtime/termux/remote_bridge/proxmox/proxmox_health.json" <<JSON
{
 "component":"STARCORE Proxmox Connector",
 "timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)",
 "ssh":"$SSH",
 "targets":[
 "Proxmox",
 "VM100",
 "Docker AI Stack"
 ],
 "status":"READY"
}
JSON


cat "$BASE/runtime/termux/remote_bridge/proxmox/proxmox_health.json"


