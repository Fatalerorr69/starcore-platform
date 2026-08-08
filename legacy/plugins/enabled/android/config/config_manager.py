#!/usr/bin/env python3


import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"


OUT=ROOT/"runtime/android/config"

OUT.mkdir(
parents=True,
exist_ok=True
)


config={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Config Manager",

"version":
"6B.X.25",

"environment":
"termux-android",

"mode":
"production",

"status":
"active"

}


json.dump(
config,
open(
OUT/"system_config.json",
"w"
),
indent=4
)


print(
"CONFIG MANAGER COMPLETE"
)


