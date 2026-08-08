#!/data/data/com.termux/files/usr/bin/bash

echo
echo "================================="
echo " STARCORE SYSTEM MODULE"
echo "================================="

echo
echo "Hostname:"
hostname

echo
echo "Kernel:"
uname -r

echo
echo "Android:"
getprop ro.build.version.release

echo
echo "Device:"
getprop ro.product.model

echo
echo "CPU:"
uname -m

echo
echo "Memory:"
free -h 2>/dev/null || true

