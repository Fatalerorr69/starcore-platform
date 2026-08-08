#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


CHECKS={

"state":
"runtime/android/state/core_state.json",

"runtime":
"runtime/android/runtime/runtime_manager.json",

"health":
"runtime/android/health/health_daemon.json",

"events":
"runtime/android/events/history.json",

"recovery":
"runtime/android/recovery/recovery_report.json"

}


OUT=ROOT/"runtime/android/controller"

OUT.mkdir(
parents=True,
exist_ok=True
)



status={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Android Core Controller",

"version":
"6B.X.3.E",

"components":{}

}



healthy=True


for name,path in CHECKS.items():

    exists=(ROOT/path).exists()

    status["components"][name]=exists

    if not exists:
        healthy=False



status["status"]=(
"operational"
if healthy
else
"degraded"
)



with open(
OUT/"system_status.json",
"w"
) as f:

    json.dump(
    status,
    f,
    indent=4
    )


print(
"CORE CONTROLLER COMPLETE"
)

