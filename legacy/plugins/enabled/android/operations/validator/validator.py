#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


files=[

"runtime/android/operations/operations_center.json",

"runtime/android/operations/execution_registry.json",

"runtime/android/operations/operation_policy.json",

"runtime/android/operations/operations_audit.json"

]


checks=[]

errors=0


for f in files:

    ok=(ROOT/f).exists()

    checks.append(
    {
    "file":f,
    "exists":ok
    }
    )

    if not ok:
        errors+=1



OUT=ROOT/"runtime/android/operations/reports"


OUT.mkdir(parents=True,exist_ok=True)


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Operations Validator",

"version":
"6B.Y.40",

"checks":
checks,

"errors":
errors,

"status":
"production" if errors==0 else "failed"

}



with open(
OUT/"operations_validation.json",
"w"
) as f:

    json.dump(
    report,
    f,
    indent=4
    )


print("OPERATIONS VALIDATION COMPLETE")

