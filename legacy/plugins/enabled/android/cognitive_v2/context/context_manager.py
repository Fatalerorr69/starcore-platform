#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/cognitive_v2/context"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Context Manager",
"context_size":0,
"status":"online"
},
open(out/"context_state.json","w"),
indent=4)

print("CONTEXT ONLINE")
