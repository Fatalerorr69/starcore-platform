#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/autonomous/workers"

OUT.mkdir(parents=True,exist_ok=True)


workers=[
"health_worker",
"snapshot_worker",
"ai_worker"
]


with open(
OUT/"workers.json",
"w"
) as f:

 json.dump(
 {
 "timestamp":datetime.now().isoformat(),
 "workers":workers,
 "status":"ready"
 },
 f,
 indent=4
 )


print("WORKER ENGINE READY")
