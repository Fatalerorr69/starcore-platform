#!/data/data/com.termux/files/usr/bin/bash

while true
do
clear

echo "==============================="
echo " STARCORE LIVE MONITOR"
echo "==============================="

echo
date

echo
echo "Memory"
free -h

echo
echo "Storage"
df -h

echo
echo "Battery"
termux-battery-status 2>/dev/null

echo
echo "Git"

git status --short

sleep 5

done
