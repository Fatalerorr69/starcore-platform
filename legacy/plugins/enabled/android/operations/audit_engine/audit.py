#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


checks=[

"runtime/android/master/master_status.json",

"runtime/android/release/STARCORE_ANDROID_1.0_RELEASE.json",

"runtime/android/remote_intelligence/remote_state.json",

"runtime/android/ai_bridge/bridge_state.json"

]


result=[]


for item in checks:

    result.append(
    {
    "file":item,
    "exists":(ROOT/item).exists()
    }
    )


OUT=ROOT/"runtime/android/operations"


with open(
OUT/"operations_audit.json",
"w"
) as f:

    json.dump(
    {
    "timestamp":datetime.now().isoformat(),
    "component":"STARCORE Operations Audit",
    "version":"6B.Y.34",
    "checks":result
    },
    f,
    indent=4
    )


print("AUDIT COMPLETE")

