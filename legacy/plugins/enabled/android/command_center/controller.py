#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/"STARCORE"

OUT=ROOT/"runtime/android/command_center"

OUT.mkdir(parents=True,exist_ok=True)


data={

"timestamp":datetime.now().isoformat(),

"component":
"STARCORE Distributed Command Center",

"version":
"6B.Y.9",

"commands":0,

"status":
"online"

}


json.dump(
data,
open(OUT/"command_center.json","w"),
indent=4
)


print("COMMAND CENTER ONLINE")

