#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


snap={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Repair Snapshot",

"version":
"6B.X.17",

"state":

"before_repair"


}



OUT=ROOT/"runtime/android/snapshots/repair"

OUT.mkdir(
parents=True,
exist_ok=True
)


name=datetime.now().strftime(
"%Y%m%d_%H%M%S.json"
)


with open(
OUT/name,
"w"
) as f:

    json.dump(
    snap,
    f,
    indent=4
    )


print(
"SNAPSHOT CREATED"
)

