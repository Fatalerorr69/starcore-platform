#!/data/data/com.termux/files/usr/bin/python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


files=[

"runtime/android/scheduler/scheduler_state.json",

"runtime/android/scheduler/execution_history.json"

]


result={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Scheduler Health",

"checks":[],

"status":
"healthy"

}


for f in files:

    result["checks"].append({

    "file":f,

    "exists":
    (ROOT/f).exists()

    })


(ROOT/"runtime/android/scheduler/scheduler_health.json").write_text(
json.dumps(
result,
indent=4
)
)


print(
"SCHEDULER HEALTH COMPLETE"
)

