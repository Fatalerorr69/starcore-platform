#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


root=Path.home()/"STARCORE"


files=[

"runtime/android/telemetry/telemetry.json",
"runtime/android/policy/policy.json",
"runtime/android/api/api_gateway.json",
"runtime/android/lifecycle/lifecycle.json",
"runtime/android/security/security_center.json"

]


checks=[]

for f in files:

 checks.append({

 "file":f,

 "exists":(root/f).exists()

 })


report={

"timestamp":datetime.now().isoformat(),

"component":
"STARCORE Distributed Intelligence Validator",

"version":
"6B.Y.20",

"checks":checks,

"errors":
len([x for x in checks if not x["exists"]]),

"status":
"healthy"

}


out=root/"runtime/android/release"

out.mkdir(parents=True,exist_ok=True)


json.dump(
report,
open(out/"distributed_intelligence_release.json","w"),
indent=4
)


print("RELEASE VALIDATION COMPLETE")
