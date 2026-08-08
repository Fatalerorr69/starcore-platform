#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/compute_fabric/scheduler"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Workload Scheduler",
"queue":[],
"status":"online"
},
open(out/"workload_queue.json","w"),
indent=4
)

print("WORKLOAD SCHEDULER ONLINE")
