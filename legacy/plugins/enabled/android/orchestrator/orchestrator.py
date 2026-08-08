#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


MODULES=ROOT/"plugins/enabled/android"

OUT=ROOT/"runtime/android/orchestration"


OUT.mkdir(
    parents=True,
    exist_ok=True
)


modules=[]


for p in MODULES.iterdir():

    if p.is_dir():

        modules.append({
            "module":p.name,
            "enabled":True
        })


state={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Orchestrator",

"version":
"6B.X.7.A",

"modules":
modules,

"status":
"running"

}


with open(
OUT/"orchestrator_state.json",
"w"
) as f:

    json.dump(
        state,
        f,
        indent=4
    )


print(
"ORCHESTRATOR READY"
)

