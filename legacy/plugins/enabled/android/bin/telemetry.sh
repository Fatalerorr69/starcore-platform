#!/data/data/com.termux/files/usr/bin/bash


ROOT="$HOME/STARCORE"

DB="$ROOT/core/database/android/android.db"


NOW=$(date -Iseconds)


MODEL=$(getprop ro.product.model 2>/dev/null || echo unknown)

ANDROID=$(getprop ro.build.version.release 2>/dev/null || echo unknown)

KERNEL=$(uname -r)

ARCH=$(uname -m)


# CPU SAFE

CPU=$(cat /proc/loadavg 2>/dev/null || echo unknown)


# MEMORY SAFE

MEM=$(free -h 2>/dev/null | tr '\n' ' ')


# STORAGE SAFE

STORAGE=$(df -h "$HOME" 2>/dev/null | tail -1)


# BATTERY SAFE

BATTERY="unknown"


if command -v termux-battery-status >/dev/null 2>&1
then

BATTERY=$(timeout 5 termux-battery-status 2>/dev/null || echo timeout)

fi



python - <<PY

import sqlite3


db="$DB"


conn=sqlite3.connect(db)

cur=conn.cursor()


cur.execute(
"""
INSERT INTO device
(timestamp,model,android,kernel,architecture)
VALUES (?,?,?,?,?)
""",
(
"$NOW",
"$MODEL",
"$ANDROID",
"$KERNEL",
"$ARCH"
)
)



cur.execute(
"""
INSERT INTO telemetry
(timestamp,cpu,memory,storage,battery)
VALUES (?,?,?,?,?)
""",
(
"$NOW",
'''$CPU''',
'''$MEM''',
"$STORAGE",
'''$BATTERY'''
)
)



conn.commit()

conn.close()


print("Telemetry stored")


PY


