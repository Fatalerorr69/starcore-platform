#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


ROOT=Path.home()/ "STARCORE"

OUT=ROOT/"runtime/android/bootstrap"

OUT.mkdir(
    parents=True,
    exist_ok=True
)


modules=[]

base=ROOT/"plugins/enabled/android"


for x in base.iterdir():
    if x.is_dir():
        modules.append(x.name)


data={

"timestamp":
datetime.now().isoformat(),

"component":
"STARCORE Bootstrap Engine",

"version":
"6B.X.22",

"modules_detected":
len(modules),

"modules":
modules,

"status":
"ready"

}


json.dump(
data,
open(
OUT/"bootstrap_status.json",
"w"
),
indent=4
)


print(
"BOOTSTRAP COMPLETE"
)

