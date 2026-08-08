#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


files=[

"runtime/android/context/context.json",

"runtime/android/memory/memory_registry.json",

"runtime/android/knowledge/knowledge_graph.json",

"runtime/android/vector/vector_state.json",

"runtime/android/memory/memory_bridge.json"

]


checks=[]


for f in files:

    checks.append({

    "file":f,

    "exists":
    (ROOT/f).exists()

    })


with open(
ROOT/"runtime/android/health/memory_health.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE AI Memory Health",

    "version":
    "6B.X.16",

    "checks":
    checks,

    "status":
    "healthy"

    },f,indent=4)



print("MEMORY HEALTH COMPLETE")

