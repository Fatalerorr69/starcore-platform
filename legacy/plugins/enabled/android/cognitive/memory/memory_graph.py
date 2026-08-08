#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/cognitive/memory"

OUT.mkdir(
parents=True,
exist_ok=True
)


memory={

"timestamp":
datetime.now().isoformat(),

"type":
"memory_graph",

"nodes":[
"device",
"runtime",
"security",
"network",
"agent"
],

"edges":[
["device","runtime"],
["runtime","agent"],
["security","device"]
]

}


with open(
OUT/"memory_graph.json",
"w"
) as f:

    json.dump(
        memory,
        f,
        indent=4
    )


print(
"MEMORY GRAPH COMPLETE"
)

