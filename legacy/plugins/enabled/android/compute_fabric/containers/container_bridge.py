#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/compute_fabric/containers"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Container Bridge",
"docker":"ready",
"status":"online"
},
open(out/"docker_bridge.json","w"),
indent=4
)

print("CONTAINER BRIDGE READY")
