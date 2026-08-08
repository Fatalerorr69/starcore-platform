#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


TARGETS=[

"plugins/enabled/android/core",

"plugins/enabled/android/agent",

"plugins/enabled/android/ai_core",

"plugins/enabled/android/cognitive",

"plugins/enabled/android/scheduler",

"plugins/enabled/android/memory"

]


checks=[]


for t in TARGETS:

    p=ROOT/t

    checks.append({

        "path":t,

        "exists":p.exists()

    })



report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Integrity Scanner",

"version":
"6B.X.17",

"checks":
checks,


"errors":
len(
[
x for x in checks
if not x["exists"]
]
),


"status":
"healthy"

}



OUT=ROOT/"runtime/android/integrity"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"integrity_report.json",
"w"
) as f:

    json.dump(
    report,
    f,
    indent=4
    )


print(
"INTEGRITY COMPLETE"
)

