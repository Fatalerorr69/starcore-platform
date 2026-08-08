#!/usr/bin/env python3

import json
from pathlib import Path
from datetime import datetime


root=Path.home()/"STARCORE"

out=root/"runtime/android/remote_api"
out.mkdir(parents=True,exist_ok=True)


data={
"timestamp":datetime.now().isoformat(),
"component":"STARCORE Remote API Gateway",
"version":"6B.Y.24",
"authentication":"enabled",
"endpoints":[
"health",
"status",
"command",
"agents"
],
"status":"secure"
}


json.dump(
data,
open(out/"remote_gateway.json","w"),
indent=4
)

print("REMOTE API READY")
