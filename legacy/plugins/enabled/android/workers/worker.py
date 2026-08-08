#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/workers"

OUT.mkdir(
parents=True,
exist_ok=True
)


result={

"timestamp":
datetime.now().isoformat(),

"worker":
"android-worker-01",

"status":
"idle",

"executed":
[]

}


with open(
OUT/"worker_status.json",
"w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print(
"WORKER READY"
)

