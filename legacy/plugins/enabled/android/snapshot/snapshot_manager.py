#!/usr/bin/env python3


import json
import shutil
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"


SRC=ROOT/"runtime/android"

OUT=ROOT/"runtime/android/snapshots"


OUT.mkdir(
parents=True,
exist_ok=True
)



snapshot={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Snapshot Manager",

"version":
"6B.X.3.G",

"files":[]

}



targets=[

"state",
"health",
"events",
"controller",
"recovery"

]


for t in targets:

    p=SRC/t

    if p.exists():

        snapshot["files"].append(
            str(p)
        )



file=OUT/(
"snapshot_"+
datetime.now()
.strftime("%Y%m%d_%H%M%S")
+
".json"
)



with open(file,"w") as f:

    json.dump(
    snapshot,
    f,
    indent=4
    )


print(
"SNAPSHOT COMPLETE"
)

print(file)

