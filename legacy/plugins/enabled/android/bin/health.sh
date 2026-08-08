#!/data/data/com.termux/files/usr/bin/bash

ROOT="$HOME/STARCORE"

echo
echo "================================="
echo " STARCORE ANDROID HEALTH"
echo "================================="


echo

echo "[DEVICE]"

getprop ro.product.model


echo

echo "[ANDROID]"

getprop ro.build.version.release


echo

echo "[SECURITY PATCH]"

getprop ro.build.version.security_patch


echo

echo "[KERNEL]"

uname -r


echo

echo "[ARCH]"

uname -m


echo

echo "[TERMUX]"

if command -v termux-info >/dev/null
then

termux-info | head -20

else

echo "Termux API unavailable"

fi


echo

echo "[ROOT]"

id


echo

echo "[STORAGE]"

df -h "$HOME"


