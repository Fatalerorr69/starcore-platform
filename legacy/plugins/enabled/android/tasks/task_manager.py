#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/tasks"

OUT.mkdir(
parents=True,
exist_ok=True
)


queue=[

{
"task":"health_scan",
"status":"queued"
},

{
"task":"module_validation",
"status":"queued"
}

]


with open(
OUT/"task_queue.json",
"w"
) as f:

    json.dump(
        {
        "timestamp":datetime.now().isoformat(),
        "tasks":queue
        },
        f,
        indent=4
    )


print(
"TASK QUEUE READY"
)

