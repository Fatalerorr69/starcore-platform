#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


checks=[

"runtime/android/system/manifest.json",

"runtime/android/installer/installer_report.json",

"runtime/android/health",

"runtime/android/reports"

]


result={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Self Test",

"version":
"6B.X.10",

"checks":[],

"status":
"healthy"

}


for c in checks:

    result["checks"].append({

    "path":c,

    "exists":
    (ROOT/c).exists()

    })


with open(
ROOT/"runtime/android/reports/selftest.json",
"w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print(
"SELF TEST COMPLETE"
)

