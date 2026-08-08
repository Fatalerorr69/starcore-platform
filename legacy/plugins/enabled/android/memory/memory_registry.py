#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


memory={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Memory Registry",

"entries":[

{
"id":1,
"type":"system",
"value":"STARCORE Android Core"
}

]

}



OUT=ROOT/"runtime/android/memory"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"memory_registry.json",
"w"
) as f:

    json.dump(
    memory,
    f,
    indent=4
    )


print("MEMORY REGISTRY READY")

