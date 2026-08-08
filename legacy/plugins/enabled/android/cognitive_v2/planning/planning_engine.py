#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/cognitive_v2/planning"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Planning Engine",
"plans":[],
"status":"online"
},
open(out/"planning_state.json","w"),
indent=4)

print("PLANNING ONLINE")
