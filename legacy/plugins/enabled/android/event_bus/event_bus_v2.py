#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/event_bus"

OUT.mkdir(parents=True,exist_ok=True)


bus={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Event Bus V2",

"version":
"6B.X.33",

"events":0,

"queue":[],

"status":
"active"

}


with open(
OUT/"event_bus.json",
"w"
) as f:

    json.dump(
        bus,
        f,
        indent=4
    )


print("EVENT BUS V2 READY")

