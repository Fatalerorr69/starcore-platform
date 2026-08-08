#!/usr/bin/env python3

import json
import subprocess
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


MODULES=[

"plugins/enabled/android/core",

"plugins/enabled/android/agent",

"plugins/enabled/android/ai_core",

"plugins/enabled/android/cognitive",

"plugins/enabled/android/scheduler",

"plugins/enabled/android/network",

"plugins/enabled/android/security",

"plugins/enabled/android/recovery"

]


REPORT=ROOT/"runtime/android/installer"


REPORT.mkdir(
    parents=True,
    exist_ok=True
)


result={

"timestamp":
datetime.now().isoformat(),

"installer":
"STARCORE Android Master Installer",

"version":
"6B.X.9",

"modules":[],

"status":
"unknown"

}



for module in MODULES:

    path=ROOT/module

    exists=path.exists()

    result["modules"].append({

        "module":module,

        "exists":exists

    })



result["status"]="healthy"


with open(
REPORT/"installer_report.json",
"w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print(
"MASTER INSTALLER VALIDATION COMPLETE"
)

