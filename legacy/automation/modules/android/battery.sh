#!/data/data/com.termux/files/usr/bin/bash

echo
echo "================================="
echo " STARCORE BATTERY"
echo "================================="

if command -v termux-battery-status >/dev/null; then
    termux-battery-status
else
    echo "Termux API not installed"
fi
