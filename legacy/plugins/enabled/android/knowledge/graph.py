#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


graph={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Knowledge Graph",

"nodes":[

"android",

"starcore",

"fatalab",

"ai"

],


"relations":[

"android->starcore",

"starcore->fatalab",

"starcore->ai"

]

}


OUT=ROOT/"runtime/android/knowledge"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"knowledge_graph.json",
"w"
) as f:

    json.dump(
    graph,
    f,
    indent=4
    )


print("KNOWLEDGE GRAPH READY")

