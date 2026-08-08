#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/autonomous_core/state"

OUT.mkdir(parents=True,exist_ok=True)

data={
"timestamp":datetime.now().isoformat(),
"component":"Autonomous Core Bootstrap",
"version":"6B.Y.91",
"status":"online"
}

with open(OUT/"bootstrap_state.json","w") as f:
    json.dump(data,f,indent=4)

print("BOOTSTRAP ONLINE")
