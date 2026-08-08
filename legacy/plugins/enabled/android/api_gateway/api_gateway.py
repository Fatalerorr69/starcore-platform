#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


root=Path.home()/"STARCORE"

out=root/"runtime/android/api"
out.mkdir(parents=True,exist_ok=True)


api={

"timestamp":datetime.now().isoformat(),

"component":
"STARCORE API Gateway",

"endpoints":[

"health",
"status",
"agents",
"memory",
"command"

],

"bridge":
"FataLab-ready",

"status":
"online"

}


json.dump(
api,
open(out/"api_gateway.json","w"),
indent=4
)

print("API GATEWAY ONLINE")
