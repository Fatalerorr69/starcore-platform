#!/data/data/com.termux/files/usr/bin/bash


ROOT="$HOME/STARCORE"

OUT="$ROOT/runtime/android/snapshots/android_snapshot_$(date +%Y%m%d_%H%M%S).json"



safe_battery(){

if command -v timeout >/dev/null 2>&1
then

timeout 3 termux-battery-status 2>/dev/null || echo '{"status":"unavailable"}'

else

echo '{"status":"no-timeout"}'

fi

}



BATTERY=$(safe_battery)



MEM=$(free -h 2>/dev/null | tr '\n' ' ')

STORAGE=$(df -h "$HOME" 2>/dev/null | tail -1)



BOOT=$(getprop ro.boot.verifiedbootstate 2>/dev/null || echo unknown)

PATCH=$(getprop ro.build.version.security_patch 2>/dev/null || echo unknown)

SELINUX=$(getenforce 2>/dev/null || echo unknown)



MAGISK=false

if [ -d /data/adb ]
then
MAGISK=true
fi



cat > "$OUT" <<JSON
{
 "timestamp":"$(date -Iseconds)",

 "device":{
   "model":"$(getprop ro.product.model)",
   "android":"$(getprop ro.build.version.release)",
   "kernel":"$(uname -r)",
   "arch":"$(uname -m)"
 },

 "resources":{
   "memory":"$MEM",
   "storage":"$STORAGE",
   "battery":$BATTERY
 },

 "security":{
   "verified_boot":"$BOOT",
   "security_patch":"$PATCH",
   "selinux":"$SELINUX",
   "magisk":$MAGISK
 },

 "ai":{
   "status":"pending",
   "recommendations":[]
 }

}
JSON


echo
echo "SNAPSHOT CREATED:"
echo "$OUT"

