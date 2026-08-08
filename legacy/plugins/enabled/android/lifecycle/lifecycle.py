#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


root=Path.home()/"STARCORE"

out=root/"runtime/android/lifecycle"
out.mkdir(parents=True,exist_ok=True)


state={

"timestamp":datetime.now().isoformat(),

"component":
"STARCORE Lifecycle Manager",

"states":[

"installed",
"validated",
"running",
"recoverable"

],

"status":
"ready"

}


json.dump(
state,
open(out/"lifecycle.json","w"),
indent=4
)

print("LIFECYCLE READY")
