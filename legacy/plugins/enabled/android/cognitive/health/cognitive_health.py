#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


FILES=[

ROOT/"runtime/android/cognitive/context/context.json",

ROOT/"runtime/android/cognitive/memory/memory_graph.json",

ROOT/"runtime/android/cognitive/vector/vector_state.json",

ROOT/"runtime/android/cognitive/router/router.json",

ROOT/"runtime/android/cognitive/bridge/fatalab_bridge.json"

]


result={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Cognitive Health",

"checks":[],

"status":
"healthy"

}


for f in FILES:

    result["checks"].append({

    "file":
    str(f),

    "exists":
    f.exists()

    })


if not all(
x["exists"]
for x in result["checks"]
):

    result["status"]="degraded"



OUT=ROOT/"runtime/android/cognitive/health"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"cognitive_health.json",
"w"
) as f:

    json.dump(
        result,
        f,
        indent=4
    )


print(
"COGNITIVE HEALTH COMPLETE"
)

