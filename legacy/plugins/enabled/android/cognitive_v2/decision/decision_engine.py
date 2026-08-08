#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/cognitive_v2/decisions"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Decision Engine",
"decisions":[],
"status":"online"
},
open(out/"decision_history.json","w"),
indent=4)

print("DECISION ONLINE")
