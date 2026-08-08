#!/data/data/com.termux/files/usr/bin/bash


ROOT="$HOME/STARCORE"

DB="$ROOT/core/database/android/android.db"


NOW=$(date -Iseconds)


BOOT=$(getprop ro.boot.verifiedbootstate 2>/dev/null || echo unknown)

LOCKED=$(getprop ro.boot.flash.locked 2>/dev/null || echo unknown)

PATCH=$(getprop ro.build.version.security_patch 2>/dev/null || echo unknown)

BUILD=$(getprop ro.build.display.id 2>/dev/null || echo unknown)


SELINUX="unknown"

if command -v getenforce >/dev/null 2>&1
then
SELINUX=$(getenforce)
fi


MAGISK="false"


if [ -d /data/adb ]
then
MAGISK="true"
fi


ROOT_STATUS="false"


if command -v su >/dev/null 2>&1
then

ROOT_STATUS="true"

fi



python - <<PY

import sqlite3


db="$DB"


conn=sqlite3.connect(db)

cur=conn.cursor()



cur.execute(
"""
INSERT INTO security
(timestamp,boot_state,selinux,magisk)
VALUES (?,?,?,?)
""",
(
"$NOW",
"boot=$BOOT locked=$LOCKED patch=$PATCH build=$BUILD root=$ROOT_STATUS",
"$SELINUX",
"$MAGISK"
)
)



conn.commit()

conn.close()


print("Security telemetry stored")

PY


