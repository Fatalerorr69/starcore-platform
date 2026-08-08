#!/data/data/com.termux/files/usr/bin/bash


echo
echo "================================="
echo " STARCORE ANDROID SECURITY AUDIT"
echo "================================="


echo

echo "Boot state:"
getprop ro.boot.verifiedbootstate


echo

echo "Bootloader:"
getprop ro.boot.flash.locked


echo

echo "SELinux:"
getenforce 2>/dev/null || echo unknown


echo

echo "Magisk:"

if [ -d /data/adb ]
then

echo "Magisk detected"

else

echo "Magisk not detected"

fi


