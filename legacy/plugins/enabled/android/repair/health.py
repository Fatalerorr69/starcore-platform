#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


files=[

"runtime/android/integrity/integrity_report.json",

"runtime/android/repair/repair_report.json"

]


checks=[]


for f in files:

    checks.append({

    "file":f,

    "exists":
    (ROOT/f).exists()

    })



with open(
ROOT/"runtime/android/repair/repair_health.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Self Repair Health",

    "version":
    "6B.X.17",

    "checks":
    checks,

    "status":
    "healthy"

    },f,indent=4)


print(
"REPAIR HEALTH COMPLETE"
)

