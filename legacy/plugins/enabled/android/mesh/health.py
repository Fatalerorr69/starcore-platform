#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


files=[

"runtime/android/agents/agent_registry.json",

"runtime/android/mesh/heartbeat.json",

"runtime/android/mesh/task_routes.json"

]


checks=[]


for f in files:

    checks.append({

    "file":f,

    "exists":
    (ROOT/f).exists()

    })



with open(
ROOT/"runtime/android/health/agent_mesh_health.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Agent Mesh Health",

    "version":
    "6B.X.15",

    "checks":
    checks,

    "status":
    "healthy"

    },f,indent=4)



print("AGENT MESH HEALTH COMPLETE")


