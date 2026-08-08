#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT = Path.home() / "STARCORE"


FILES=[

"runtime/android/registry/module_registry.json",

"runtime/android/health/runtime_status.json",

"runtime/android/health/config_validation.json"

]


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Android Core",

"version":
"6B.X.2.1",

"checks":[],

"status":
"healthy"

}


for f in FILES:

    path=ROOT/f

    report["checks"].append(

        {
        "file":f,
        "exists":path.exists()
        }

    )

    if not path.exists():

        report["status"]="warning"



OUT=ROOT/"runtime/android/health/health_report.json"


with open(
OUT,
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print(
"HEALTH CHECK COMPLETE"
)

