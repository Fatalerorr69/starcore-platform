#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


agents=[

{
"name":"core-agent",
"type":"controller",
"status":"online"
},

{
"name":"health-agent",
"type":"monitor",
"status":"online"
},

{
"name":"scheduler-agent",
"type":"executor",
"status":"online"
},

{
"name":"ai-agent",
"type":"decision",
"status":"online"
}

]


OUT=ROOT/"runtime/android/agents"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"agent_registry.json",
"w"
) as f:

    json.dump({

    "timestamp":
    datetime.now().isoformat(),

    "component":
    "STARCORE Agent Registry",

    "version":
    "6B.X.15",

    "agents":
    agents

    },f,indent=4)


print("AGENT REGISTRY READY")

