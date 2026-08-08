#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/cognitive/context"

OUT.mkdir(
    parents=True,
    exist_ok=True
)


context={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Cognitive Context Engine",

"device_context":
str(
ROOT/"runtime/android/context/device_context.json"
),

"active":
True

}


with open(
OUT/"context.json",
"w"
) as f:

    json.dump(
        context,
        f,
        indent=4
    )


print(
"CONTEXT ENGINE COMPLETE"
)

