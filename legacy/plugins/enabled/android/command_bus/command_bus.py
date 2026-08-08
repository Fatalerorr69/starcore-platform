#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


root=Path.home()/"STARCORE"

out=root/"runtime/android/command_bus"
out.mkdir(parents=True,exist_ok=True)


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Command Bus",
"version":"6B.Y.23",
"queue":[],
"history":[],
"status":"online"
}


json.dump(
data,
open(out/"command_registry.json","w"),
indent=4
)

print("COMMAND BUS ONLINE")
