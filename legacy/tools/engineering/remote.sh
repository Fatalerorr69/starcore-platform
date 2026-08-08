#!/data/data/com.termux/files/usr/bin/bash

BASE="$HOME/STARCORE"

echo "========== REMOTE STATUS =========="

cat "$BASE/runtime/termux/remote_bridge/control/control_registry.json" 2>/dev/null

echo

cat "$BASE/runtime/access/proxmox_registry.json" 2>/dev/null
