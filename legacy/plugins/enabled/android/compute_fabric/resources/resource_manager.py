#!/usr/bin/env python3

import json
import os
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/compute_fabric/resources"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Resource Manager",
"cpu_count":os.cpu_count(),
"status":"online"
},
open(out/"resource_state.json","w"),
indent=4
)

print("RESOURCE MANAGER ONLINE")
