#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


CHECKS=[

"runtime/android/fabric/fabric_state.json",

"runtime/android/control/controller_status.json",

"runtime/android/scheduler/scheduler_health.json",

"runtime/android/cognitive/health/cognitive_health.json"

]


result=[]


for c in CHECKS:

    result.append({

    "file":c,

    "exists":
    (ROOT/c).exists()

    })


status=all(
x["exists"] for x in result
)


OUT=ROOT/"runtime/android/health"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"global_health.json",
"w"
) as f:

    json.dump(

    {

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Global Health",

    "version":
    "6B.X.13",

    "checks":
    result,

    "status":
    "healthy" if status else "degraded"

    },

    f,

    indent=4

    )


print(
"GLOBAL HEALTH COMPLETE"
)

