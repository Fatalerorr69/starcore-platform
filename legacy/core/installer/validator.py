#!/usr/bin/env python3

import json
import os
from datetime import datetime

BASE=os.path.expanduser("~/STARCORE")

files=[
"runtime/platform/installer_state.json",
"registry/modules.json"
]

checks=[]

errors=0

for item in files:
    exists=os.path.exists(f"{BASE}/{item}")

    checks.append({
        "file":item,
        "exists":exists
    })

    if not exists:
        errors+=1


health={
    "timestamp":datetime.utcnow().isoformat(),
    "component":"STARCORE Installer Framework Validator",
    "version":"7.0.01",
    "checks":checks,
    "errors":errors,
    "status":"healthy" if errors==0 else "failed"
}


with open(
f"{BASE}/runtime/platform/health.json",
"w"
) as f:
    json.dump(health,f,indent=4)


print("VALIDATOR COMPLETE")
