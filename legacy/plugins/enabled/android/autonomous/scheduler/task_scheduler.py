#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/autonomous/scheduler"

OUT.mkdir(parents=True,exist_ok=True)


tasks=[
{
"name":"health_check",
"interval":300,
"enabled":True
},
{
"name":"snapshot",
"interval":3600,
"enabled":True
},
{
"name":"ai_analysis",
"interval":900,
"enabled":True
}
]


with open(
OUT/"scheduler.json",
"w"
) as f:

 json.dump(
 {
 "timestamp":datetime.now().isoformat(),
 "tasks":tasks
 },
 f,
 indent=4
 )


print("SCHEDULER READY")
