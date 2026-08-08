#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/\
"STARCORE"


OUT=ROOT/"runtime/android/audit"


OUT.mkdir(
parents=True,
exist_ok=True
)



report={

"timestamp":
datetime.now().isoformat(),

"checks":{

"magisk":

Path("/data/adb").exists(),


"zygisk":

Path("/data/adb/modules").exists(),


"bootloader":

"unknown"

},

"notes":[

"Read only audit",

"No automatic modification"

]

}



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
"INTEGRITY AUDIT COMPLETE"
)

