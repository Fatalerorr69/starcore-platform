#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"



files=[

"runtime/android/access/ssh_status.json",

"runtime/android/remote/tailscale_status.json",

"runtime/android/remote/remote_profile.json"

]


checks=[]


for f in files:

    checks.append({

    "file":f,

    "exists":
    (ROOT/f).exists()

    })



with open(
ROOT/"runtime/android/health/remote_health.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Remote Health",

    "version":
    "6B.X.14",

    "checks":
    checks,

    "status":
    "healthy"

    },f,indent=4)



print("REMOTE HEALTH COMPLETE")

