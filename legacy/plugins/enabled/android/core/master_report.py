#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


REPORTS=[

ROOT/"runtime/android/security/security_report.json",

ROOT/"runtime/android/network/network_report_v2.json",

ROOT/"runtime/android/audit/integrity_report.json",

ROOT/"runtime/android/reports/android_ai_report.json",

ROOT/"runtime/android/optimization/optimization_report.json"

]


OUT=ROOT/"runtime/android/master"

OUT.mkdir(
    parents=True,
    exist_ok=True
)



master={

"timestamp":
datetime.now().isoformat(),

"module":
"STARCORE Android Intelligence Core",

"version":
"6B.X.1",

"components":{}

}



for report in REPORTS:

    if report.exists():

        try:

            with open(report) as f:

                master["components"][report.name]=json.load(f)

        except:

            master["components"][report.name]="invalid"



with open(
OUT/"android_master_report.json",
"w"
) as f:

    json.dump(
        master,
        f,
        indent=4
    )


print(
"MASTER REPORT CREATED"
)

