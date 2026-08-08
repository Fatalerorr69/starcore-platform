#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/autonomous_core/state"

OUT.mkdir(parents=True,exist_ok=True)

state={
"timestamp":datetime.now().isoformat(),
"component":"Global State Controller",
"version":"6B.Y.92",
"nodes":"managed",
"status":"online"
}

with open(OUT/"global_state.json","w") as f:
    json.dump(state,f,indent=4)

print("STATE CONTROLLER ONLINE")
