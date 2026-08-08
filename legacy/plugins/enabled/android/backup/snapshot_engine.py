#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


OUT=ROOT/"runtime/android/backup"

OUT.mkdir(
parents=True,
exist_ok=True
)


snapshot={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Snapshot Engine",

"version":
"6B.X.24",

"scope":
[
"plugins/enabled/android",
"runtime/android"
],

"type":
"logical_snapshot",

"status":
"created"

}



json.dump(
snapshot,
open(
OUT/"latest_snapshot.json",
"w"
),
indent=4
)


print(
"SNAPSHOT COMPLETE"
)


