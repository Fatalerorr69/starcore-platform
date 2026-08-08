#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT=Path.home()/ "STARCORE"


checks=[

"runtime/android/autonomous_core/state/bootstrap_state.json",
"runtime/android/autonomous_core/state/global_state.json",
"runtime/android/autonomous_core/missions/mission_registry.json",
"runtime/android/autonomous_core/decisions/decision_state.json",
"runtime/android/autonomous_core/optimization/optimization_state.json",
"runtime/android/autonomous_core/sync/sync_state.json",
"runtime/android/autonomous_core/events/event_state.json",
"runtime/android/autonomous_core/recovery/recovery_state.json",
"runtime/android/autonomous_core/supervisor/supervisor_state.json"

]


result={

"timestamp":datetime.now().isoformat(),

"component":
"STARCORE Autonomous Intelligence Platform",

"version":
"6B.Y.100",

"modules":
100,

"checks":[],

"errors":0,

"status":
"PRODUCTION"

}


for item in checks:

    exists=Path(item).exists()

    result["checks"].append(
        {
        "file":item,
        "exists":exists
        }
    )

    if not exists:
        result["errors"]+=1


if result["errors"]>0:
    result["status"]="FAILED"


OUT=ROOT/"runtime/android/release"

OUT.mkdir(parents=True,exist_ok=True)


with open(
OUT/"STARCORE_6BYY100_MASTER_RELEASE.json",
"w"
) as f:

    json.dump(result,f,indent=4)


print("MASTER RELEASE VALIDATION COMPLETE")

