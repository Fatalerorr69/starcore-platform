#!/data/data/com.termux/files/usr/bin/bash

ROOT="$HOME/STARCORE"

REPORT="$ROOT/automation/modules/reports/device_$(date +%Y%m%d_%H%M%S).json"


cat > "$REPORT" <<JSON
{
"device":"$(getprop ro.product.model)",
"android":"$(getprop ro.build.version.release)",
"security_patch":"$(getprop ro.build.version.security_patch)",
"kernel":"$(uname -r)",
"architecture":"$(uname -m)",
"python":"$(python --version 2>&1)",
"storage":"$(df -h $HOME | tail -1)"
}
JSON


echo
echo "REPORT CREATED:"
echo "$REPORT"

