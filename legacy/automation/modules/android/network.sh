#!/data/data/com.termux/files/usr/bin/bash

echo
echo "================================="
echo " STARCORE NETWORK"
echo "================================="

echo
echo "IP:"
ip addr show 2>/dev/null | grep inet || true

echo
echo "Connectivity:"
ping -c 1 github.com >/dev/null 2>&1

if [ $? -eq 0 ]; then
echo "ONLINE"
else
echo "OFFLINE"
fi

