#!/usr/bin/env python3


import json
import os
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


metrics={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Metrics",

"storage":{

"total":
os.statvfs("/").f_frsize *
os.statvfs("/").f_blocks,

"free":
os.statvfs("/").f_frsize *
os.statvfs("/").f_bavail

}

}


OUT=ROOT/"runtime/android/metrics"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"metrics.json",
"w"
) as f:

    json.dump(
    metrics,
    f,
    indent=4
    )


print(
"METRICS COMPLETE"
)

