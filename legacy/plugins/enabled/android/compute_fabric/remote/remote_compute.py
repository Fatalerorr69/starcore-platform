#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime

out=Path.home()/ "STARCORE/runtime/android/compute_fabric/remote"

out.mkdir(parents=True,exist_ok=True)

json.dump(
{
"timestamp":datetime.now().isoformat(),
"component":"Remote Compute Connector",
"nodes":[
"ANDROID",
"FATALAB"
],
"status":"ready"
},
open(out/"compute_nodes.json","w"),
indent=4
)

print("REMOTE COMPUTE READY")
