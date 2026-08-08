#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


context={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Context Store",

"version":
"6B.X.16",

"context":{

"device":"android",

"core":"STARCORE",

"mode":"autonomous"

}

}


OUT=ROOT/"runtime/android/context"

OUT.mkdir(
parents=True,
exist_ok=True
)


with open(
OUT/"context.json",
"w"
) as f:

    json.dump(
    context,
    f,
    indent=4
    )


print("CONTEXT READY")

