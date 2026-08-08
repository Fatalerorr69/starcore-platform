#!/data/data/com.termux/files/usr/bin/bash

echo
echo "================================="
echo " STARCORE ANDROID MODULE"
echo "================================="

echo
echo "Android:"
getprop ro.build.version.release

echo
echo "Security patch:"
getprop ro.build.version.security_patch

echo
echo "Boot state:"
getprop ro.boot.verifiedbootstate

echo
echo "Root:"
id

