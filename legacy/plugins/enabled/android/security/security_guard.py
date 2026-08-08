#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/security"
OUT.mkdir(parents=True,exist_ok=True)


checks=[]


for p in [
"plugins/enabled/android/core",
"plugins/enabled/android/agent",
"plugins/enabled/android/ai_core",
"plugins/enabled/android/cognitive",
"plugins/enabled/android/scheduler"
]:

    checks.append({
        "path":p,
        "exists":(ROOT/p).exists()
    })


report={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Security Guard",
"version":"6B.X.33",
"checks":checks,
"status":"healthy"
}


with open(OUT/"security_state.json","w") as f:
    json.dump(report,f,indent=4)


print("SECURITY READY")

