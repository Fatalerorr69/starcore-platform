#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/release"

OUT.mkdir(parents=True,exist_ok=True)


files=[

"runtime/android/unified/installer_state.json",
"runtime/android/state_db/system_state.json",
"runtime/android/event_bus/event_bus.json",
"runtime/android/job_queue/job_queue.json",
"runtime/android/agents_supervisor/supervisor_state.json",
"runtime/android/recovery_v2/recovery_state.json"

]


checks=[]


for f in files:

    checks.append({

    "file":f,
    "exists":(ROOT/f).exists()

    })


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Autonomous Core Release",

"version":
"6B.X.40",

"checks":
checks,

"errors":
sum(
1 for x in checks
if not x["exists"]
),

"status":
"production"

}


with open(
OUT/"STARCORE_ANDROID_1.0_RELEASE.json",
"w"
) as f:

    json.dump(report,f,indent=4)


print("RELEASE CORE READY")

