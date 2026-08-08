#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/memory_fabric/short_term"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Short Term Memory",
"items":0,
"status":"online"
},
open(out/"short_memory.json","w"),
indent=4
)

print("SHORT MEMORY ONLINE")
