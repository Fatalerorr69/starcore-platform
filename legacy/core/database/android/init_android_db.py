#!/usr/bin/env python3

import sqlite3
from pathlib import Path


ROOT = Path.home() / "STARCORE"

DB = ROOT / "core/database/android/android.db"


DB.parent.mkdir(
    parents=True,
    exist_ok=True
)


conn = sqlite3.connect(DB)

cur = conn.cursor()


cur.execute("""
CREATE TABLE IF NOT EXISTS device (
id INTEGER PRIMARY KEY,
timestamp TEXT,
model TEXT,
android TEXT,
kernel TEXT,
architecture TEXT
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS telemetry (
id INTEGER PRIMARY KEY,
timestamp TEXT,
cpu TEXT,
memory TEXT,
storage TEXT,
battery TEXT
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS security (
id INTEGER PRIMARY KEY,
timestamp TEXT,
boot_state TEXT,
selinux TEXT,
magisk TEXT
)
""")


conn.commit()

conn.close()


print(DB)

