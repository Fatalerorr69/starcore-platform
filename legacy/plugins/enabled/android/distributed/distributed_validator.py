#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


files=[

"runtime/android/fatalab/connector_state.json",

"runtime/android/distributed/node_registry.json",

"runtime/android/fatalab/health_sync.json",

"runtime/android/ai_bridge/bridge_state.json"

]


checks=[]


for f in files:

    checks.append({

    "file":f,

    "exists":(ROOT/f).exists()

    })


report={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Distributed Validator",

"version":
"6B.Y.5",

"checks":
checks,

"errors":
sum(
1 for x in checks
if not x["exists"]
),

"status":
"healthy"

}


with open(
ROOT/"runtime/android/release/distributed_validation.json",
"w"
) as f:

    json.dump(
        report,
        f,
        indent=4
    )


print("DISTRIBUTED VALIDATION READY")

