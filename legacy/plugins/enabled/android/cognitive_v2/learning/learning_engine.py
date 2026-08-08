#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/cognitive_v2/learning"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Learning Engine",
"patterns":0,
"status":"online"
},
open(out/"learning_state.json","w"),
indent=4)

print("LEARNING ONLINE")
