#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/compute_fabric/cpu"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"CPU Monitor",
"load":"unknown",
"status":"monitoring"
},
open(out/"cpu_metrics.json","w"),
indent=4
)

print("CPU MONITOR ONLINE")
