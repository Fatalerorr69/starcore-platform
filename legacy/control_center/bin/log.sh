#!/data/data/com.termux/files/usr/bin/bash

LOG="$HOME/STARCORE/control_center/logs/control.log"

echo "$(date '+%F %T') | $*" >> "$LOG"

