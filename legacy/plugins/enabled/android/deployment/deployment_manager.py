#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


MODULE_ROOT=ROOT/"plugins/enabled/android"


OUT=ROOT/"runtime/android/deployments"


OUT.mkdir(
    parents=True,
    exist_ok=True
)


modules=[]


for x in MODULE_ROOT.iterdir():

    if x.is_dir():

        modules.append(
            {
            "module":x.name,
            "available":True
            }
        )


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Deployment Manager",

"version":
"6B.X.10",

"modules":
modules,

"status":
"ready"

}


with open(
OUT/"deployment_report.json",
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print(
"DEPLOYMENT MANAGER READY"
)

