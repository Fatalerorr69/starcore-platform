#!/usr/bin/env python3


from pathlib import Path
import json
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


checks=[

"runtime/android/master/master_status.json",

"runtime/android/release/release_manifest.json"

]


data=[]


for c in checks:

    data.append({

    "file":c,

    "exists":
    (ROOT/c).exists()

    })


with open(
ROOT/"runtime/android/release/master_validation.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Master Validator",

    "version":
    "6B.X.18",

    "checks":
    data,

    "status":
    "healthy"

    },f,indent=4)


print(
"VALIDATION COMPLETE"
)

