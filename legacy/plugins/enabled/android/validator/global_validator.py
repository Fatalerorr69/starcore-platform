#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


OUT=ROOT/"runtime/android/validator"

OUT.mkdir(
parents=True,
exist_ok=True
)


targets=[

"runtime/android/foundation/foundation_health.json",

"runtime/android/master/master_status.json",

"runtime/android/control/controller_status.json",

"runtime/android/scheduler/scheduler_health.json",

"runtime/android/cognitive/health/cognitive_health.json"

]


checks=[]


for t in targets:

    checks.append({

    "file":t,

    "exists":
    Path(t).exists()

    })


errors=sum(
1 for c in checks
if not c["exists"]
)



report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Global Validator",

"version":
"6B.X.23",

"checks":
checks,

"errors":
errors,

"status":
"healthy"
if errors==0
else "warning"

}



json.dump(
report,
open(
OUT/"global_validation.json",
"w"
),
indent=4
)


print(
"GLOBAL VALIDATION COMPLETE"
)

