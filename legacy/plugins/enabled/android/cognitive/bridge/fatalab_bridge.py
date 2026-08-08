#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/cognitive/bridge"

OUT.mkdir(
parents=True,
exist_ok=True
)


bridge={

"timestamp":
datetime.now().isoformat(),

"bridge":
"Android -> FataLab",

"target":
"AI Core VM",

"connection":
"not configured",

"status":
"prepared"

}


with open(
OUT/"fatalab_bridge.json",
"w"
) as f:

    json.dump(
        bridge,
        f,
        indent=4
    )


print(
"FATALAB BRIDGE COMPLETE"
)

