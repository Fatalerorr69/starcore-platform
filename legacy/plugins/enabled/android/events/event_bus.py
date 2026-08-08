#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/events"
OUT.mkdir(parents=True,exist_ok=True)


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Event Bus",
"version":"6B.X.32",
"queue":[],
"subscribers":[],
"status":"online"
}


with open(OUT/"bus_state.json","w") as f:
    json.dump(data,f,indent=4)


print("EVENT BUS READY")

