#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


agents=[

"core-agent",
"health-agent",
"scheduler-agent",
"ai-agent"

]


status=[]


for a in agents:

    status.append({

    "agent":a,

    "heartbeat":
    datetime.now().isoformat(),

    "status":
    "alive"

    })


OUT=ROOT/"runtime/android/mesh"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"heartbeat.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Agent Heartbeat",

    "agents":
    status

    },f,indent=4)



print("HEARTBEAT COMPLETE")

